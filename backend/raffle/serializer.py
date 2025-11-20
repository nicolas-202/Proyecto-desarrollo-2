from rest_framework import serializers
from django.utils import timezone
from .models import Raffle
from user.serializer import UserBasicSerializer
from raffleInfo.serializer import PrizeTypeSerializer, StateRaffleSerializer
from django.core.exceptions import ValidationError 

class RaffleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear nuevas rifas
    Estado se asigna automáticamente a nivel del modelo
    """
    raffle_image = serializers.ImageField(required=False)  
    
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
            'raffle_prize_amount',
            'raffle_prize_type',
        ]

    def validate_raffle_draw_date(self, value):
        #Validar que la fecha del sorteo sea futura
        if value <= timezone.now():
            raise serializers.ValidationError("La fecha del sorteo debe ser futura")
        return value
        
    def validate(self, data):
        # Validar que el mínimo de números vendidos no exceda la cantidad total
        if data['raffle_minimum_numbers_sold'] > data['raffle_number_amount']:
            raise serializers.ValidationError("El mínimo de números vendidos no puede ser mayor que la cantidad total de números")
        return data
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['raffle_created_by'] = request.user
        
        # Crear la rifa (el modelo asignará estado automáticamente)
        return super().create(validated_data)
        
class RaffleListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar rifas
    """
    raffle_prize_type = PrizeTypeSerializer(read_only=True)
    raffle_state = StateRaffleSerializer(read_only=True)
    raffle_created_by = UserBasicSerializer(read_only=True)
    class Meta:
        model = Raffle
        fields = [
            'id',
            'raffle_name',
            'raffle_description',
            'raffle_draw_date',
            'raffle_minimum_numbers_sold',
            'raffle_number_amount',
            'raffle_number_price',
            'raffle_image',
            'raffle_prize_amount',
            'raffle_prize_type',
            'raffle_state',
            'raffle_created_by',
        ]

class RaffleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer SEGURO para actualizar rifas
    Solo permite modificar campos que no afecten la integridad del negocio
    """
    raffle_image = serializers.ImageField(required=False)  # Opcional para actualizaciones
    
    class Meta:
        model = Raffle
        fields = [
            'raffle_name',                    
            'raffle_description',              
            'raffle_draw_date',              
            'raffle_minimum_numbers_sold',   
            'raffle_image',                  
            
        ]
        
    def validate_raffle_draw_date(self, value):
        """
        Validación ESTRICTA para fecha del sorteo
        """
        now = timezone.now()
        
        if value <= now:
            raise serializers.ValidationError("La fecha del sorteo debe ser futura")
        
        if self.instance and self.instance.raffle_draw_date:
            time_until_current_draw = self.instance.raffle_draw_date - now
            if time_until_current_draw.total_seconds() < 86400:  # 24 horas en segundos
                raise serializers.ValidationError(
                    "No se puede cambiar la fecha cuando faltan menos de 24 horas para el sorteo"
                )
        
        return value
        
    def validate_raffle_minimum_numbers_sold(self, value):
        """
        Validación para números mínimos vendidos
        """
        if self.instance:
            # No permitir aumentar el mínimo si ya se vendieron números
            numbers_sold = self.instance.numbers_sold  # Propiedad del modelo
            if value > self.instance.raffle_number_amount:
                raise serializers.ValidationError(
                    "El mínimo no puede ser mayor que la cantidad total de números"
                )
            
            # Si ya hay ventas, no permitir aumentar el mínimo por encima de lo vendido
            if numbers_sold > 0 and value > numbers_sold:
                raise serializers.ValidationError(
                    f"No se puede establecer un mínimo de {value} cuando solo se han vendido {numbers_sold} números"
                )
                
        return value
        
    def validate(self, data):
        """
        Validaciones globales de seguridad
        """
        # Si existe la instancia, verificar que no esté en estado crítico
        if self.instance:
            # No permitir cambios si ya tiene ganador
            if self.instance.raffle_winner:
                raise serializers.ValidationError("No se puede modificar una rifa que ya fue sorteada")
            
            # No permitir cambios si está inactiva (usando estado)
            if not self.instance._is_in_active_state():
                raise serializers.ValidationError("No se puede modificar una rifa inactiva")
        
        return data
        
    
class AdminRaffleUpdateSerializer(serializers.ModelSerializer):

    raffle_image = serializers.ImageField(required=False)  # Opcional para actualizaciones
    
    class Meta:
        model = Raffle
        fields = [
            'raffle_name',                    
            'raffle_description',              
            'raffle_draw_date',
            'raffle_start_date',         
            'raffle_image',
            'raffle_minimum_numbers_sold',   
            'raffle_prize_type',            
            'raffle_state',             
        ]
    def validate_raffle_draw_date(self, value):
        # Los admins pueden establecer fechas en el pasado si es necesario
        # (útil para migrar rifas históricas o corregir errores)
        if value <= timezone.now():
            # Solo advertencia, no error para admins
            print(f"Warning: Admin estableciendo fecha de sorteo en el pasado: {value}")
        
        return value
    
    def validate_raffle_minimum_numbers_sold(self, value):
        # Los admins pueden establecer mínimos "imposibles" con advertencia
        if self.instance and value > self.instance.raffle_number_amount:
            # Admin puede hacerlo, pero con advertencia
            print(f"Warning: Admin estableciendo mínimo ({value}) mayor que total ({self.instance.raffle_number_amount})")
        
        return value


class RaffleSoftDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer para soft delete de rifas
    Cambia el estado de la rifa a inactivo en lugar de eliminarla físicamente
    """
    
    class Meta:
        model = Raffle
        fields = ['id']
        read_only_fields = ['id']
    
    def update(self, instance, validated_data):
        """
        Implementa el soft delete cambiando el estado a inactivo
        """
        from raffleInfo.models import StateRaffle
        
        # Verificar que la rifa no tenga un ganador (ya fue sorteada)
        if instance.raffle_winner:
            raise serializers.ValidationError(
                "No se puede eliminar una rifa que ya fue sorteada"
            )
        
        try:
            # Buscar estado inactivo por código
            inactive_state = StateRaffle.objects.filter(
                state_raffle_code__iexact='INA'
            ).first()
            
            if not inactive_state:
                # Buscar por nombre si no encuentra por código
                inactive_state = StateRaffle.objects.filter(
                    state_raffle_name__icontains='inactiv'
                ).first()
            
            if not inactive_state:
                raise serializers.ValidationError(
                    "No se encontró un estado inactivo válido en el sistema"
                )
            
            # Cambiar estado a inactivo
            instance.raffle_state = inactive_state
            instance.save()
            
            return instance
            
        except Exception as e:
            raise serializers.ValidationError(
                f"Error al realizar soft delete: {str(e)}"
            )
    

class RaffleDrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raffle
        fields = ['id']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        """Ejecutar sorteo de la rifa"""
        try:
            # Usar método del modelo para sorteo
            result = instance.execute_raffle_draw()
            return instance, result
        except (ValidationError, ValueError) as e:
            raise serializers.ValidationError(str(e))


class AvailableNumbersSerializer(serializers.ModelSerializer):
    """
    Serializer para obtener números disponibles de una rifa
    """
    available_numbers = serializers.ListField(read_only=True)
    numbers_sold = serializers.IntegerField(read_only=True)
    numbers_available = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Raffle
        fields = [
            'id',
            'raffle_name',
            'raffle_number_amount',
            'raffle_number_price',
            'available_numbers',
            'numbers_sold', 
            'numbers_available'
        ]