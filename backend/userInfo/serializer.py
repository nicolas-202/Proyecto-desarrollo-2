from rest_framework import serializers
from .models import DocumentType, Gender, PaymentMethodType, PaymentMethod
from django.utils import timezone

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'  

class PaymentMethodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodType
        fields = '__all__'

class PaymentMethodSerializer(serializers.ModelSerializer):
    # Campo virtual para recibir el número de tarjeta sin hashear
    card_number = serializers.CharField(
        write_only=True, 
        max_length=19,
        required=False,  # No obligatorio para actualizaciones parciales
        allow_blank=False,  # No permitir vacío cuando se proporciona
        help_text="Número de tarjeta (será hasheado automáticamente)"
    )
    
    # Campos de solo lectura
    masked_card_number = serializers.SerializerMethodField()
    payment_method_type_name = serializers.CharField(
        source='payment_method_type.payment_method_type_name', 
        read_only=True
    )

    class Meta:
        model = PaymentMethod
        fields = (
            'id',
            'payment_method_type',
            'payment_method_type_name',
            'paymenth_method_holder_name',
            'card_number',  # Solo para escribir
            'masked_card_number',  # Solo para leer
            'paymenth_method_expiration_date',
            'last_digits',
            'payment_method_is_active',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'last_digits', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'paymenth_method_holder_name': {
                'required': False,  # No obligatorio para actualizaciones parciales
                'allow_blank': False,
                'help_text': 'Nombre del titular de la tarjeta'
            },
            'paymenth_method_expiration_date': {
                'required': False,  # No obligatorio para actualizaciones parciales
                'help_text': 'Fecha de expiración (YYYY-MM-DD)'
            }
        }

    def get_masked_card_number(self, obj):
        """Retorna el número de tarjeta enmascarado"""
        return obj.get_masked_card_number()

    def validate_card_number(self, value):
        """Validar número de tarjeta"""
        if not value or not value.strip():
            raise serializers.ValidationError("El número de tarjeta es obligatorio.")
        
        # Remover espacios y guiones
        card_number = value.replace(' ', '').replace('-', '')
        
        # Validar que solo contenga números
        if not card_number.isdigit():
            raise serializers.ValidationError("El número de tarjeta solo debe contener números.")
        
        # Validar longitud (13-19 dígitos para tarjetas reales)
        if not (13 <= len(card_number) <= 19):
            raise serializers.ValidationError("El número de tarjeta debe tener entre 13 y 19 dígitos.")
        
        return card_number

    def validate_paymenth_method_expiration_date(self, value):
        """Validar que la fecha no sea pasada y sea obligatoria"""
        if not value:
            raise serializers.ValidationError("La fecha de expiración es obligatoria.")
            
        if value < timezone.now().date():
            raise serializers.ValidationError("La fecha de expiración no puede ser en el pasado.")
        return value

    def validate_paymenth_method_holder_name(self, value):
        """Validar nombre del titular"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre del titular es obligatorio.")
            
        cleaned_value = value.strip()
        if len(cleaned_value) < 2:
            raise serializers.ValidationError("El nombre del titular debe tener al menos 2 caracteres.")
            
        if len(cleaned_value) > 100:
            raise serializers.ValidationError("El nombre del titular no puede exceder 100 caracteres.")
            
        return cleaned_value.title()

    def validate(self, data):
        """Validaciones a nivel de objeto"""
        # Solo verificar campos obligatorios en creación, no en actualización
        if not self.instance:  # Es creación
            required_fields = ['card_number', 'paymenth_method_holder_name', 'paymenth_method_expiration_date']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    raise serializers.ValidationError(f"El campo {field} es obligatorio.")
        
        return data

    def create(self, validated_data):
        """Crear método de pago"""
        card_number = validated_data.pop('card_number')
        user = self.context['request'].user
        
        payment_method = PaymentMethod(**validated_data)
        payment_method.user = user
        payment_method.set_card_number(card_number)
        payment_method.save()
        
        return payment_method

    def update(self, instance, validated_data):
        """Actualizar método de pago"""
        card_number = validated_data.pop('card_number', None)
        
        # Actualizar otros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Si se proporciona nuevo número de tarjeta, hashearlo
        if card_number:
            instance.set_card_number(card_number)
        
        instance.save()
        return instance