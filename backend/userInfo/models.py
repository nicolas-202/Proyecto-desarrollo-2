from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from user.models import User

# Create your models here.
class DocumentType(models.Model):
    document_type_name = models.CharField(max_length=50, unique=True)
    document_type_code = models.CharField(max_length=4, unique=True)
    document_type_description= models.TextField(blank=True, null=True)
    document_type_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.document_type_name
    
class Gender(models.Model):
    gender_name = models.CharField(max_length=50, unique=True)
    gender_code = models.CharField(max_length=4, unique=True)
    gender_description= models.TextField(blank=True, null=True)
    gender_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.gender_name

class PaymentMethodType(models.Model):
    payment_method_type_name = models.CharField(max_length=50, unique=True)
    payment_method_type_code = models.CharField(max_length=4, unique=True)
    payment_method_type_description= models.TextField(blank=True, null=True)
    payment_method_type_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.payment_method_type_name
    
class PaymentMethod(models.Model):
    payment_method_type = models.ForeignKey(
        PaymentMethodType,
        on_delete=models.RESTRICT,
        verbose_name='Tipo de método de pago'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario propietario',
        related_name='payment_methods'
    )
    paymenth_method_holder_name = models.CharField(
        max_length=100,
        verbose_name='Titular de la forma de pago',
        blank=False,  # No permitir vacío en formularios
        null=False    # No permitir NULL en BD
    )
    paymenth_method_card_number_hash = models.CharField(
        max_length=128,
        verbose_name='Número de tarjeta hasheado',
        blank=False,
        null=False
    )
    paymenth_method_expiration_date = models.DateField(
        verbose_name='Fecha de expiración',
        blank=False,
        null=False
    )
    last_digits = models.CharField(
        max_length=4,
        verbose_name='Últimos 4 dígitos'
    )
    # Nuevo campo saldo para simulación
    payment_method_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name='Saldo disponible',
        help_text='Saldo disponible para simulación - Solo manejable desde BD'
    )
    payment_method_is_active = models.BooleanField(
        default=True,
        verbose_name='Estado activo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Método de pago'
        verbose_name_plural = 'Métodos de pago'
        ordering = ['-created_at']

    def set_card_number(self, raw_card_number):
        """
        Hashea el número de tarjeta usando el mismo método que las contraseñas
        """
        self.paymenth_method_card_number_hash = make_password(raw_card_number)
        # Extraer últimos 4 dígitos antes de hashear
        self.last_digits = raw_card_number[-4:] if len(raw_card_number) >= 4 else raw_card_number

    def check_card_number(self, raw_card_number):
        """
        Verifica si el número de tarjeta coincide con el hasheado
        """
        return check_password(raw_card_number, self.paymenth_method_card_number_hash)

    def get_masked_card_number(self):
        """
        Retorna el número de tarjeta enmascarado para mostrar
        """
        return f"**** **** **** {self.last_digits}"

    def has_sufficient_balance(self, amount):
        """
        Verifica si hay saldo suficiente para una transacción
        """
        return self.payment_method_balance >= amount

    def deduct_balance(self, amount):
        """
        Deducir saldo (para simulación de transacciones)
        Solo debe usarse internamente, no desde la API
        """
        if self.has_sufficient_balance(amount):
            self.payment_method_balance -= amount
            self.save()
            return True
        return False

    def add_balance(self, amount):
        """
        Agregar saldo (para simulación de recargas)
        Solo debe usarse internamente, no desde la API
        """
        print(f"[DEBUG add_balance] Antes: id={id(self)}, saldo={self.payment_method_balance}, monto a agregar={amount}")
        self.payment_method_balance += amount
        self.save()
        print(f"[DEBUG add_balance] Después: id={id(self)}, saldo={self.payment_method_balance}")

    def get_balance_display(self):
        """
        Retorna el saldo formateado para mostrar
        """
        return f"${self.payment_method_balance:,.2f}"

    def __str__(self):
        return f"{self.payment_method_type.payment_method_type_name} - {self.get_masked_card_number()} ({self.paymenth_method_holder_name}) - {self.get_balance_display()}"

    def save(self, *args, **kwargs):
        """
        Validar que la fecha de expiración no sea pasada
        """
        from django.utils import timezone
        if self.paymenth_method_expiration_date and self.paymenth_method_expiration_date < timezone.now().date():
            raise ValueError("La fecha de expiración no puede ser en el pasado")
        super().save(*args, **kwargs)