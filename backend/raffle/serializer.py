from rest_framework import serializers
from django.utils import timezone
from .models import Raffle
from raffleInfo.serializer import PrizeTypeSerializer, StateRaffleSerializer

class RaffleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear nuevas rifas
    """
    raffle_image = serializers.ImageField(required=False)  # Hacer opcional
    
    class Meta: 
        model = Raffle
        fields = [
            'raffle_name',
            'raffle_description',
            'raffle_draw_date',
            'raffle_minimum_numbers_sold',
            'raffle_number_amount',
            'raffle_number_price',
            'raffle_image',
            'raffle_price_amount',
            'raffle_prize_type',
            'raffle_state',
        ]

    def validate_raffle_draw_date(self, value):
        """Validar que la fecha del sorteo sea futura"""
        if value <= timezone.now():
            raise serializers.ValidationError("La fecha del sorteo debe ser futura")
        return value
        
    def validate(self, data):
        if data['raffle_minimum_numbers_sold'] > data['raffle_number_amount']:
            raise serializers.ValidationError("El mínimo de números vendidos no puede ser mayor que la cantidad total de números")
        return data
        
    def create(self, validated_data):
        from django.core.files.base import ContentFile
        from django.conf import settings
        import os
        import uuid
        
        request = self.context.get('request')
        if request and request.user:
            validated_data['raffle_created_by'] = request.user
        
        # Crear la rifa primero
        raffle = super().create(validated_data)
        
        # Si no se proporcionó imagen, asignar la imagen por defecto después de crear
        if not raffle.raffle_image:
            default_image_path = os.path.join(settings.MEDIA_ROOT, 'raffles', 'defaults', 'default_raffle.jpg')
            print(f"Buscando imagen por defecto en: {default_image_path}")  # Debug
            
            if os.path.exists(default_image_path):
                print("Imagen por defecto encontrada, asignando...")  # Debug
                try:
                    with open(default_image_path, 'rb') as f:
                        image_content = f.read()
                    
                    # Crear nombre único para evitar conflictos
                    unique_name = f"raffle_{raffle.id}_default_{uuid.uuid4().hex[:8]}.jpg"
                    
                    # Asignar la imagen
                    raffle.raffle_image.save(
                        unique_name,
                        ContentFile(image_content),
                        save=True
                    )
                    print(f"Imagen asignada: {raffle.raffle_image.name}")  # Debug
                    
                except Exception as e:
                    print(f"Error al asignar imagen por defecto: {e}")  # Debug
            else:
                print("Imagen por defecto no encontrada")  # Debug
        
        return raffle
        
