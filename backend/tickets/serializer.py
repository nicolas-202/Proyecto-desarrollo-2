from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Ticket
from raffle.models import Raffle
from userInfo.models import PaymentMethod
from user.serializer import UserBasicSerializer
from userInfo.serializer import PaymentMethodSerializer

class TicketCreateSerializer(serializers.ModelSerializer):#Serializer para compra de tickets
    raffle_id = serializers.IntegerField(write_only=True)
    payment_method_id = serializers.IntegerField(write_only=True)
    number = serializers.IntegerField()
    
    class Meta:
        model = Ticket
        fields = ['raffle_id', 'payment_method_id', 'number']

    def validate_raffle_id(self, value): #Validar que la rifa existe y está activa
        try:
            raffle = Raffle.objects.get(id=value)
            if not raffle.is_active_for_sales:
                raise serializers.ValidationError("La rifa no está activa para ventas")
            return value
        except Raffle.DoesNotExist:
            raise serializers.ValidationError("La rifa especificada no existe")

    def validate_payment_method_id(self, value):#Validar que el método de pago existe y pertenece al usuario

        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Usuario no autenticado")
        
        try:
            payment_method = PaymentMethod.objects.get(id=value, user=request.user)
            return value
        except PaymentMethod.DoesNotExist:
            raise serializers.ValidationError("Método de pago no válido o no pertenece al usuario")

    def validate(self, data):#otras validaciones 
        raffle = Raffle.objects.get(id=data['raffle_id'])
        number = data['number']
        
        # Validar rango del número
        if number < 1 or number > raffle.raffle_number_amount:
            raise serializers.ValidationError(f"El número debe estar entre 1 y {raffle.raffle_number_amount}")
        
        # Validar que el número esté disponible
        if number not in raffle.available_numbers:
            raise serializers.ValidationError(f"El número {number} no está disponible")
        
        return data

    def create(self, validated_data): #Crear ticket usando el método del modelo
        request = self.context.get('request')
        user = request.user
        
        raffle = Raffle.objects.get(id=validated_data['raffle_id'])
        payment_method = PaymentMethod.objects.get(id=validated_data['payment_method_id'])
        number = validated_data['number']
        
        try:
            # Usar el método del modelo Ticket para la compra
            ticket = Ticket.purchase_ticket(user, raffle, number, payment_method)
            return ticket
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))


class TicketListSerializer(serializers.ModelSerializer): #Serializer para listar tickets con información expandida
    user = UserBasicSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    raffle_name = serializers.CharField(source='raffle.raffle_name', read_only=True)
    raffle_id = serializers.IntegerField(source='raffle.id', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id',
            'number',
            'is_winner',
            'created_at',
            'user',
            'payment_method',
            'raffle_id',
            'raffle_name'
        ]


class TicketRefundSerializer(serializers.ModelSerializer): #Serializer para reembolsar tickets individuales
    class Meta:
        model = Ticket
        fields = ['id']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        try:
            # Usar método del modelo para reembolso
            instance.refund_ticket()
            return instance  # El objeto ya fue eliminado, pero devolvemos referencia
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))

