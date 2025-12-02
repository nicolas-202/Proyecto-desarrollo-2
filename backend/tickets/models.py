from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
import random
from user.models import User
from userInfo.models import PaymentMethod


class Ticket(models.Model): 
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchased_tickets',
        verbose_name='Usuario'
    )
    
    raffle = models.ForeignKey(
        'raffle.Raffle',
        on_delete=models.CASCADE,
        related_name='sold_tickets',
        verbose_name='Rifa'
    )
    
    number = models.PositiveIntegerField(
        verbose_name='Número del ticket'
    )
    
    is_winner = models.BooleanField(
        default=False,
        verbose_name='Es ganador'
    )
    
    # Método de pago usado para comprar este ticket
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,  # No eliminar método si tiene tickets
        related_name='purchased_tickets',
        verbose_name='Método de pago usado',
        help_text='Método de pago con el que se compró este ticket'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de compra'
    )

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        unique_together = ['raffle', 'number']  # Un número por rifa
        ordering = ['-created_at']

    def clean(self):
        if self.raffle and self.number:
            # Validar rango
            if self.number < 1 or self.number > self.raffle.raffle_number_amount:
                raise ValidationError(f'Número debe estar entre 1 y {self.raffle.raffle_number_amount}')
            # Validar que la rifa esté activa solo para tickets nuevos (no ganadores)
            if not self.is_winner and not self.raffle.is_active_for_sales:
                raise ValidationError('La rifa no está activa para ventas')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        winner = " 🏆" if self.is_winner else ""
        return f'#{self.number:03d} - {self.raffle.raffle_name} - {self.user.email} ({self.payment_method.payment_method_type}){winner}'

    @classmethod
    def purchase_ticket(cls, user, raffle, number, payment_method):
        # Validar que el método de pago pertenezca al usuario
        if payment_method.user != user:
            raise ValidationError("El método de pago no pertenece al usuario")
        # Validar saldo suficiente
        if not payment_method.has_sufficient_balance(raffle.raffle_number_price):
            raise ValidationError(f"Saldo insuficiente. Necesitas ${raffle.raffle_number_price}")
        # Validar número disponible
        if number not in raffle.available_numbers:
            raise ValidationError(f"El número {number} no está disponible")

        # Buscar cuenta conjunta de admin
        from user.models import User
        from userInfo.models import PaymentMethod
        try:
            admin_user = User.objects.filter(document_number="0000000000").first()
            if not admin_user:
                raise ValidationError("No existe usuario admin con identificación 0000000000 para cuenta conjunta")
            admin_account = PaymentMethod.objects.filter(user=admin_user, payment_method_is_active=True).first()
            if not admin_account:
                raise ValidationError("No existe método de pago activo para admin")
            success = payment_method.deduct_balance(raffle.raffle_number_price)
            if success:
                admin_account.add_balance(raffle.raffle_number_price)
            else:
                raise ValidationError("Error al procesar el pago")
        except Exception as e:
            raise ValidationError(f"Error en cuenta conjunta admin: {e}")
        # Crear el ticket
        ticket = cls.objects.create(
            user=user,
            raffle=raffle,
            number=number,
            payment_method=payment_method
        )
        return ticket
    
    def refund_ticket(self): 

        from user.models import User
        from userInfo.models import PaymentMethod
        try:
            admin_user = User.objects.filter(document_number="0000000000").first()
            if not admin_user:
                raise ValidationError("No existe usuario admin con identificación 0000000000 para cuenta conjunta")
            admin_account = PaymentMethod.objects.filter(user=admin_user, payment_method_is_active=True).first()
            if not admin_account:
                raise ValidationError("No existe método de pago activo para admin")
            # Restar dinero de la cuenta conjunta
            admin_account.deduct_balance(self.raffle.raffle_number_price)
            # Devolver dinero al método de pago original
            self.payment_method.add_balance(self.raffle.raffle_number_price)
        except Exception as e:
            raise ValidationError(f"Error en cuenta conjunta admin: {e}")
        # Eliminar ticket de la base de datos
        self.delete()
        
        return True
