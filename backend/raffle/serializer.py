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
            'raffle_creator_payment_method',
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
    raffle_winner = UserBasicSerializer(read_only=True)
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
            'raffle_winner',
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
    """
    Serializer para ejecutar sorteo y mostrar resultados
    Si la rifa ya fue sorteada, muestra información del ganador
    """
    # Campos adicionales para mostrar información del sorteo
    winner_info = serializers.SerializerMethodField()
    draw_result = serializers.SerializerMethodField()
    is_already_drawn = serializers.SerializerMethodField()
    
    class Meta:
        model = Raffle
        fields = [
            'id', 
            'raffle_name',
            'raffle_state',
            'is_already_drawn',
            'winner_info',
            'draw_result'
        ]
        read_only_fields = ['id', 'raffle_name', 'raffle_state']

    def get_is_already_drawn(self, obj):
        """Verificar si la rifa ya fue sorteada"""
        return obj.raffle_winner is not None
    
    def get_winner_info(self, obj):
        """Obtener información del ganador si existe"""
        if not obj.raffle_winner:
            return None
        
        return {
            'winner_id': obj.raffle_winner.id,
            'winner_name': f"{obj.raffle_winner.first_name} {obj.raffle_winner.last_name}",
            'winner_email': obj.raffle_winner.email,
            'winner_phone': obj.raffle_winner.phone_number,
            'winning_number': obj.raffle_winner_ticket.number if obj.raffle_winner_ticket else None,
            'prize_amount': str(obj.raffle_prize_amount),
            'prize_type': obj.raffle_prize_type.prize_type_name,
            'draw_date': obj.raffle_draw_date,
        }
    
    def get_draw_result(self, obj):
        """Obtener resultados del último sorteo ejecutado (si está en context)"""
        # Este campo se llena cuando se ejecuta el sorteo
        return self.context.get('draw_result', None)

    def update(self, instance, validated_data):
        """Ejecutar sorteo de la rifa"""
        # Verificar si ya fue sorteada
        if instance.raffle_winner:
            raise serializers.ValidationError({
                'error': 'Esta rifa ya fue sorteada',
                'winner_info': self.get_winner_info(instance)
            })
        
        try:
            # Usar método del modelo para sorteo
            result = instance.execute_raffle_draw()
            
            # Guardar el resultado en el contexto para mostrarlo
            self.context['draw_result'] = result
            
            return instance
        except (ValidationError, ValueError) as e:
            raise serializers.ValidationError({
                'error': str(e),
                'raffle_state': instance.raffle_state.state_raffle_name if instance.raffle_state else 'Desconocido'
            })
    
    def to_representation(self, instance):
        """Personalizar la respuesta según si ya fue sorteada o se acaba de sortear"""
        representation = super().to_representation(instance)
        
        # Si hay resultado de sorteo en el contexto (sorteo recién ejecutado)
        draw_result = self.context.get('draw_result')
        if draw_result:
            representation['message'] = draw_result.get('message')
            representation['winner_user'] = draw_result.get('winner_user')
            representation['winner_number'] = draw_result.get('winner_number')
            representation['prize_amount'] = draw_result.get('prize_amount')
            representation['prize_type'] = draw_result.get('prize_type')
            representation['tickets_sold'] = draw_result.get('tickets_sold')
            representation['total_revenue'] = draw_result.get('total_revenue')
            representation['raffle_status'] = draw_result.get('raffle_status')
        
        # Agregar información del estado
        if instance.raffle_state:
            representation['raffle_state'] = {
                'id': instance.raffle_state.id,
                'name': instance.raffle_state.state_raffle_name,
                'code': instance.raffle_state.state_raffle_code
            }
        
        return representation


class AvailableNumbersSerializer(serializers.ModelSerializer):
    """
    Serializer para obtener números disponibles de una rifa
    """
    numbers = serializers.SerializerMethodField()
    numbers_sold = serializers.IntegerField(read_only=True)
    numbers_available = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Raffle
        fields = [
            'id',
            'raffle_name',
            'raffle_number_amount',
            'raffle_number_price',
            'numbers',  # array de números disponibles
            'numbers_sold', 
            'numbers_available'
        ]

    def get_numbers(self, obj):
        # Usar el método del modelo para obtener los números disponibles
        return obj.available_numbers