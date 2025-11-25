from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from permissions.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Raffle
from .serializer import (
    RaffleCreateSerializer, 
    RaffleListSerializer, 
    RaffleSoftDeleteSerializer,
    RaffleUpdateSerializer,
    RaffleDrawSerializer,
    AvailableNumbersSerializer

)
from raffleInfo.serializer import PrizeTypeSerializer, StateRaffleSerializer


class RaffleCreateView(generics.CreateAPIView):
    """
    Vista para crear nuevas rifas únicamente
    """
    serializer_class = RaffleCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Para manejar archivos de imagen
    
    def create(self, request, *args, **kwargs):
        """
        Crear una nueva rifa
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raffle = serializer.save()
        
        return Response({
            'message': 'Rifa creada exitosamente',
            'raffle_id': raffle.id,
            'raffle_name': raffle.raffle_name,
            'raffle_state': raffle.raffle_state.state_raffle_name if raffle.raffle_state else None
        }, status=status.HTTP_201_CREATED)

class RaffleListView(generics.ListAPIView):
    """
    Vista para listar todas las rifas activas con detalles expandidos
    Acceso público - no requiere autenticación
    """
    serializer_class = RaffleListSerializer
    permission_classes = [AllowAny]  # Acceso público
    
    def get_queryset(self):
        """
        Retorna solo las rifas que están en estado activo
        """
        from raffleInfo.models import StateRaffle
        
        # Obtener todos los estados que se consideren "activos"
        active_states = StateRaffle.objects.filter(
            state_raffle_code__iexact='ACT'
        )
        
        # Si no encuentra por código, buscar por nombre
        if not active_states.exists():
            active_states = StateRaffle.objects.filter(
                state_raffle_name__icontains='activ'
            )
        
        return Raffle.objects.filter(
            raffle_state__in=active_states
        ).select_related('raffle_prize_type', 'raffle_state')


class RaffleSoftDeleteView(generics.UpdateAPIView):
    """
    Vista para soft delete de rifas
    Cambia el estado de la rifa a inactivo en lugar de eliminarla
    """
    queryset = Raffle.objects.all()
    serializer_class = RaffleSoftDeleteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        """
        Realizar soft delete de la rifa CON REEMBOLSOS
        """
        instance = self.get_object()
        
        # Verificar que el usuario sea el creador de la rifa
        if instance.raffle_created_by != request.user:
            return Response({
                'error': 'Solo el creador de la rifa puede eliminarla'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Usar el nuevo método del modelo que incluye reembolsos
            result = instance.soft_delete_and_refund(request.user)
            
            return Response({
                'message': result['message'],
                'raffle_id': instance.id,
                'raffle_name': instance.raffle_name,
                'tickets_refunded': result['tickets_refunded'],
                'total_amount_refunded': str(result['total_amount_refunded']),
                'cancellation_type': result['cancellation_type'],
                'new_state': instance.raffle_state.state_raffle_name if instance.raffle_state else None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al eliminar la rifa: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class RaffleDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener el detalle de una rifa específica
    Acceso público
    """
    queryset = Raffle.objects.all().select_related('raffle_prize_type', 'raffle_state', 'raffle_created_by', 'raffle_winner')
    serializer_class = RaffleListSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class RaffleUpdateView(generics.UpdateAPIView):
    """
    Vista para actualizar rifas existentes
    Solo el creador puede actualizar
    """
    queryset = Raffle.objects.all()
    serializer_class = RaffleUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar rifa existente
        """
        instance = self.get_object()
        
        # Verificar que el usuario sea el creador de la rifa
        if instance.raffle_created_by != request.user:
            return Response({
                'error': 'Solo el creador de la rifa puede modificarla'
            }, status=status.HTTP_403_FORBIDDEN)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_instance = serializer.save()
            return Response({
                'message': 'Rifa actualizada exitosamente',
                'raffle_id': updated_instance.id,
                'raffle_name': updated_instance.raffle_name
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al actualizar la rifa: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        """
        Actualización parcial
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class RaffleUserListView(generics.ListAPIView):
    """
    Vista pública para ver rifas de un usuario específico
    Puede incluir rifas inactivas si el usuario autenticado es el mismo
    """
    serializer_class = RaffleListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Retorna rifas de un usuario específico
        """
        user_id = self.kwargs.get('user_id')
        include_inactive = self.request.query_params.get('include_inactive', 'false').lower() == 'true'
        
        # Base queryset
        queryset = Raffle.objects.filter(
            raffle_created_by_id=user_id
        ).select_related('raffle_prize_type', 'raffle_state', 'raffle_created_by')
        
        # Si no se solicitan inactivas O no es el mismo usuario, filtrar solo activas
        if not include_inactive or not self._is_same_user(user_id):
            from raffleInfo.models import StateRaffle
            
            # Obtener estados activos
            active_states = StateRaffle.objects.filter(
                state_raffle_code__iexact='ACT'
            )
            
            if not active_states.exists():
                active_states = StateRaffle.objects.filter(
                    state_raffle_name__icontains='activ'
                )
            
            queryset = queryset.filter(raffle_state__in=active_states)
        
        return queryset.order_by('-raffle_created_at')
    
    def _is_same_user(self, user_id):
        """
        Verifica si el usuario autenticado es el mismo que se está consultando
        """
        if not self.request.user.is_authenticated:
            return False
        
        try:
            return int(user_id) == self.request.user.id
        except (ValueError, TypeError):
            return False


class AdminRaffleCancelView(generics.UpdateAPIView):
    """
    Vista EXCLUSIVA para administradores
    Permite cancelar rifas con reembolsos por razones administrativas
    """
    queryset = Raffle.objects.all()
    permission_classes = [IsAdminUser]  # Solo administradores
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        """
        Cancelación administrativa con reembolsos
        """
        instance = self.get_object()
        admin_reason = request.data.get('admin_reason', 'Cancelación administrativa')
        
        try:
            # Usar método administrativo del modelo
            result = instance.cancel_raffle_and_refund(admin_reason)
            
            return Response({
                'message': result['message'],
                'raffle_id': instance.id,
                'raffle_name': instance.raffle_name,
                'tickets_refunded': result['tickets_refunded'],
                'total_amount_refunded': str(result['total_amount_refunded']),
                'admin_reason': result['admin_reason'],
                'was_previously_drawn': result['was_previously_drawn'],
                'cancellation_date': result['cancellation_date'],
                'cancelled_by_admin': request.user.email,
                'raffle_status': result['raffle_status']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error en cancelación administrativa: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        

class RaffleDrawView(generics.UpdateAPIView):
    """
    Vista para ejecutar sorteo de rifas
    Solo administradores pueden ejecutar el sorteo
    """
    queryset = Raffle.objects.all()
    serializer_class = RaffleDrawSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        """Ejecutar sorteo de la rifa"""
        instance = self.get_object()
        
        # Si la rifa ya fue sorteada, devolver información del ganador
        if instance.raffle_winner:
            serializer = self.get_serializer(instance)
            return Response({
                'message': 'Esta rifa ya fue sorteada',
                'is_already_drawn': True,
                'raffle_info': serializer.data
            }, status=status.HTTP_200_OK)
        
        try:
            # Ejecutar sorteo
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            updated_instance = serializer.save()
            
            # Serializar con el resultado del sorteo
            result_serializer = self.get_serializer(updated_instance)
            
            return Response(result_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AvailableNumbersView(generics.RetrieveAPIView):
    """
    Vista pública para obtener números disponibles de una rifa
    """
    queryset = Raffle.objects.all()
    serializer_class = AvailableNumbersSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
