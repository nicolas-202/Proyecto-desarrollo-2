from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Raffle
from .serializer import RaffleCreateSerializer


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
