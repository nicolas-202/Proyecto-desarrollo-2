from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Ticket
from .serializer import (
    TicketCreateSerializer,
    TicketListSerializer, 
    TicketRefundSerializer
)
from raffle.models import Raffle


class TicketPurchaseView(generics.CreateAPIView):
    """
    Vista para comprar tickets - Funcionalidad principal
    """
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Comprar un ticket"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            ticket = serializer.save()
            
            return Response({
                'message': 'Ticket comprado exitosamente',
                'ticket_id': ticket.id,
                'ticket_number': ticket.number,
                'raffle_name': ticket.raffle.raffle_name,
                'amount_paid': str(ticket.raffle.raffle_number_price),
                'payment_method': str(ticket.payment_method.payment_method_type),
                'purchase_date': ticket.created_at
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Error al comprar ticket: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class TicketListView(generics.ListAPIView):
    """
    Vista para listar tickets del usuario autenticado
    """
    serializer_class = TicketListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna solo los tickets del usuario autenticado"""
        return Ticket.objects.filter(
            user=self.request.user
        ).select_related('raffle', 'payment_method').order_by('-created_at')


class RaffleTicketsView(generics.ListAPIView):
    """
    Vista pública para ver todos los tickets de una rifa específica
    """
    serializer_class = TicketListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Retorna tickets de una rifa específica"""
        raffle_id = self.kwargs.get('raffle_id')
        return Ticket.objects.filter(
            raffle_id=raffle_id
        ).select_related('user', 'payment_method').order_by('number')


class TicketRefundView(generics.UpdateAPIView):
    """
    Vista para reembolsar tickets individuales
    Solo el dueño del ticket puede reembolsarlo
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketRefundSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        """Reembolsar ticket individual"""
        instance = self.get_object()
        
        # Verificar que el ticket pertenece al usuario
        if instance.user != request.user:
            return Response({
                'error': 'Solo el dueño del ticket puede reembolsarlo'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Guardar información antes del reembolso (el ticket se elimina)
            ticket_info = {
                'ticket_id': instance.id,
                'ticket_number': instance.number,
                'raffle_name': instance.raffle.raffle_name,
                'refund_amount': str(instance.raffle.raffle_number_price),
                'payment_method': str(instance.payment_method.payment_method_type)
            }
            
            # Procesar reembolso usando serializer
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'message': 'Ticket reembolsado exitosamente',
                **ticket_info
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al reembolsar ticket: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserTicketStatsView(generics.RetrieveAPIView):
    """
    Vista para obtener estadísticas de tickets del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        """Obtener estadísticas del usuario"""
        user = request.user
        
        total_tickets = Ticket.objects.filter(user=user).count()
        winning_tickets = Ticket.objects.filter(user=user, is_winner=True).count()
        active_tickets = Ticket.objects.filter(
            user=user, 
            raffle__raffle_winner__isnull=True  # Rifas sin ganador aún
        ).count()
        
        # Calcular dinero gastado
        user_tickets = Ticket.objects.filter(user=user).select_related('raffle')
        total_spent = sum(ticket.raffle.raffle_number_price for ticket in user_tickets)
        
        return Response({
            'user_email': user.email,
            'total_tickets_purchased': total_tickets,
            'winning_tickets': winning_tickets,
            'active_tickets': active_tickets,
            'total_amount_spent': str(total_spent),
            'win_rate': f"{(winning_tickets / total_tickets * 100):.1f}%" if total_tickets > 0 else "0.0%"
        }, status=status.HTTP_200_OK)


class UserTicketHistoryView(generics.ListAPIView):
    """
    Vista para listar el historial de tickets de un usuario específico
    Permite a los usuarios ver su propio historial o a los admins ver cualquier historial
    """
    serializer_class = TicketListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna tickets del usuario especificado con validaciones de permisos"""
        user_id = self.kwargs.get('user_id')
        request_user = self.request.user
        
        # Validar que el usuario especificado existe
        try:
            from user.models import User
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Ticket.objects.none()  # Retorna queryset vacío
        
        # Verificar permisos: solo el mismo usuario o staff pueden ver el historial
        if request_user.id != int(user_id) and not request_user.is_staff:
            return Ticket.objects.none()  # Sin permisos, retorna vacío
        
        # Retornar historial completo del usuario
        return Ticket.objects.filter(
            user_id=user_id
        ).select_related('raffle', 'payment_method', 'user').order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """Personalizar respuesta para incluir información del usuario consultado"""
        user_id = self.kwargs.get('user_id')
        
        # Validar permisos antes de procesar
        if request.user.id != int(user_id) and not request.user.is_staff:
            return Response({
                'error': 'No tienes permisos para ver el historial de este usuario'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from user.models import User
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener el queryset y serializarlo
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Información adicional del historial
        total_tickets = queryset.count()
        winning_tickets = queryset.filter(is_winner=True).count()
        
        return Response({
            'user_info': {
                'user_id': target_user.id,
                'user_email': target_user.email,
                'total_tickets_in_history': total_tickets,
                'winning_tickets_in_history': winning_tickets
            },
            'tickets': serializer.data
        }, status=status.HTTP_200_OK)
