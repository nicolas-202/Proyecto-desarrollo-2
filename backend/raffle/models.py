from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from raffleInfo.models import PrizeType, StateRaffle
from user.models import User
import os

def raffle_image_upload_path(instance, filename):
    # Obtener la fecha actual
    now = timezone.now()
    # Obtener la extensión del archivo y limpiar el nombre
    ext = filename.split('.')[-1].lower()
    # Limpiar el nombre original para evitar caracteres problemáticos
    clean_name = "".join(c for c in filename.split('.')[0] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_name = clean_name.replace(' ', '_')[:50]  # Limitar longitud
    
    # Crear nombre único basado en el ID de la rifa (si existe) o timestamp
    if instance.pk:
        filename = f"raffle_{instance.pk}_{clean_name}.{ext}"
    else:
        # Usar microsegundos para mayor unicidad en rifas nuevas
        filename = f"raffle_new_{now.strftime('%Y%m%d_%H%M%S_%f')}.{ext}"
    
    return os.path.join('raffles', str(now.year), str(now.month), filename)


class Raffle(models.Model):
    raffle_name = models.CharField(
        max_length=100, 
        verbose_name='Nombre de la rifa',
        help_text='Nombre de la rifa'
    )
    raffle_description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Descripción',
        help_text='Descripción detallada de la rifa'
    )
    raffle_start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha y hora de inicio',
        help_text='Fecha y hora de inicio de la rifa (se asigna automáticamente al crear)'
    )
    raffle_draw_date = models.DateTimeField(
        verbose_name='Fecha y hora del sorteo',
        help_text='Fecha y hora programada para realizar el sorteo (fin de ventas)'
    )
    raffle_minimum_numbers_sold = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Mínimo de números para sortear',
        help_text='Cantidad mínima de números que deben venderse para activar el sorteo'
    )
    raffle_number_amount = models.IntegerField(
        validators=[MinValueValidator(10)],
        verbose_name='Cantidad de números',
        help_text='Total de números disponibles para la rifa'
    )
    raffle_number_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio por número',
        help_text='Precio individual de cada número'
    )
    
    # Imagen subida al servidor (recomendada)
    raffle_image = models.ImageField(
        upload_to=raffle_image_upload_path,
        blank=True,
        null=True,
        verbose_name='Imagen de la rifa',
        help_text='Imagen promocional de la rifa (opcional)'
    )
    raffle_prize_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto del premio',
        help_text='Monto total del premio de la rifa'
    )
    raffle_prize_type = models.ForeignKey(
        PrizeType, 
        on_delete=models.RESTRICT,  
        verbose_name='Tipo de premio'
    )
    raffle_state = models.ForeignKey(
        StateRaffle, 
        on_delete=models.RESTRICT,  
        verbose_name='Estado de la rifa'
    )
    raffle_created_by = models.ForeignKey(
        User, 
        on_delete=models.RESTRICT,  
        related_name='created_raffles',
        verbose_name='Creado por'
    )
    
    raffle_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    raffle_updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    raffle_winner = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name='won_raffles',
        verbose_name='Ganador de la rifa'
    )

    class Meta:
        verbose_name = 'Rifa'
        verbose_name_plural = 'Rifas'
        ordering = ['-raffle_created_at']
        indexes = [
            models.Index(fields=['raffle_state']),
            models.Index(fields=['raffle_start_date', 'raffle_draw_date']),
            models.Index(fields=['raffle_draw_date']),
            models.Index(fields=['raffle_created_by']),
            models.Index(fields=['raffle_winner']),
            models.Index(fields=['raffle_name']),
            models.Index(fields=['raffle_prize_type'])
        ]

    def clean(self): #Validaciones personalizadas
        errors = []
        if self.raffle_start_date and self.raffle_draw_date:
            if self.raffle_start_date >= self.raffle_draw_date:
                errors.append('La fecha de inicio debe ser anterior a la fecha del sorteo')
        
        # Solo validar fecha del pasado si la rifa está activa y no ha sido procesada
        if (self.pk and self.raffle_draw_date and self.raffle_draw_date < timezone.now() 
            and not self.raffle_winner and self._is_in_active_state() 
            and not getattr(self, '_allow_past_date', False)):  # Flag para permitir cambios administrativos
            errors.append('La fecha del sorteo no puede ser en el pasado')
        
        if (self.raffle_minimum_numbers_sold and 
            self.raffle_number_amount and 
            self.raffle_minimum_numbers_sold > self.raffle_number_amount):
            errors.append('El mínimo de números para sortear no puede ser mayor al total de números disponibles')
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs): #Asignar estado activo por defecto solo si la rifa es nueva
        if not self.pk and not self.raffle_state_id:  
            self._assign_default_active_state()
        self.clean()
        super().save(*args, **kwargs)
    
    def _assign_default_active_state(self): #Asignar estado "Activo" por defecto
        from raffleInfo.models import StateRaffle
        try:
            # Buscar estado "Activo" por código
            active_state = StateRaffle.objects.filter(
                state_raffle_code__iexact='ACT'
            ).first()
            
            if not active_state:
                # Si no encuentra por código, buscar por nombre
                active_state = StateRaffle.objects.filter(
                    state_raffle_name__icontains='activ'
                ).first()
            
            if active_state:
                self.raffle_state = active_state
                print(f"Estado por defecto asignado: {active_state.state_raffle_name}")
            else:
                print("Warning: No se encontró estado 'Activo' por defecto")
                
        except Exception as e:
            print(f"Error al asignar estado por defecto: {e}")

    def _is_in_active_state(self): #Verifica si la rifa está en estado activo
        if not self.raffle_state:
            return False
        
        # Verificar por código de estado
        if self.raffle_state.state_raffle_code:
            if self.raffle_state.state_raffle_code.upper() == 'ACT':
                return True
        
        # Verificar por nombre de estado (fallback)
        if self.raffle_state.state_raffle_name:
            return 'activa' in self.raffle_state.state_raffle_name.lower()
        
        return False

    @property
    def image_url(self):#retorna la URL de la imagen si existe, sino la imagen por defecto
        if self.raffle_image:
            return self.raffle_image.url
        
        # Retornar imagen por defecto
        from django.conf import settings
        return f"{settings.MEDIA_URL}raffles/defaults/default_raffle.jpg"
    
    @property
    def numbers_sold(self): #Cantidad de números vendidos
        return self.sold_tickets.count()
    
    @property
    def numbers_available(self): #Cantidad de números disponibles
        return self.raffle_number_amount - self.numbers_sold
    
    @property
    def minimum_reached(self): #Verifica si se alcanzó el mínimo para sortear
        return self.numbers_sold >= self.raffle_minimum_numbers_sold
    
    @property
    def is_active_for_sales(self): #Verifica si la rifa está activa para ventas
        now = timezone.now()
        return (
            self._is_in_active_state() and
            self.raffle_start_date <= now < self.raffle_draw_date and
            self.numbers_available > 0 and
            not self.raffle_winner  # No ha sido sorteada
        )
    
    @property
    def is_ready_for_draw(self): #Verifica si la rifa está lista para ser sorteada
        now = timezone.now()
        return (
            self._is_in_active_state() and
            now >= self.raffle_draw_date and
            self.minimum_reached and
            not self.raffle_winner  # No ha sido sorteada aún
        )
    
    @property
    def can_be_drawn(self): #Verifica si la rifa puede ser sorteada (sin importar la fecha)
        return (
            self._is_in_active_state() and
            self.minimum_reached and
            not self.raffle_winner
        )
    
    @property
    def status_display(self): #Retorna una descripción del estado actual de la rifa
        now = timezone.now()
        
        if self.raffle_winner:
            return "Sorteada"
        elif now < self.raffle_start_date:
            return "Programada"
        elif now < self.raffle_draw_date:
            if not self.minimum_reached:
                remaining = self.raffle_minimum_numbers_sold - self.numbers_sold
                return f"Ventas activas (faltan {remaining} para alcanzar mínimo)"
            else:
                return "Ventas activas (mínimo alcanzado)"
        elif now >= self.raffle_draw_date:
            if not self.minimum_reached:
                return "Sorteo cancelado (no se alcanzó el mínimo)"
            else:
                return "Lista para sortear"
        else:
            return "Estado desconocido"

    def __str__(self): #Representación en cadena
        return self.raffle_name
    
    @property
    def available_numbers(self): #Obtiene lista de números disponibles para comprar
        sold_numbers = set(self.sold_tickets.values_list('number', flat=True))
        all_numbers = set(range(1, self.raffle_number_amount + 1))
        return sorted(list(all_numbers - sold_numbers))
    
    @property
    def sold_numbers(self):
        return list(self.sold_tickets.values_list('number', flat=True))
    
    def cancel_raffle_and_refund(self, admin_reason=None): #Cancela la rifa y devuelve dinero - Para uso administrativo
        """
        Cancela la rifa y reembolsa a todos los participantes.
        USO ADMINISTRATIVO: Para casos de incumplimiento, fraude o disputas.
        
        Permite cancelar incluso rifas ya sorteadas en casos excepcionales.
        """
        # Reembolsar todos los tickets de esta rifa
        tickets = self.sold_tickets.all()
        refunded_count = 0
        total_refunded = 0
        
        for ticket in tickets:
            # Devolver dinero al método de pago
            ticket.payment_method.add_balance(self.raffle_number_price)
            total_refunded += self.raffle_number_price
            refunded_count += 1
        
        # Eliminar todos los tickets (soft delete implícito)
        tickets.delete()
        
        # Cambiar estado a cancelado si existe
        from raffleInfo.models import StateRaffle
        try:
            cancelled_state = StateRaffle.objects.filter(
                state_raffle_code__iexact='CAN'
            ).first() or StateRaffle.objects.filter(
                state_raffle_name__icontains='cancel'
            ).first()
            
            if cancelled_state:
                self.raffle_state = cancelled_state
                self.save()
        except Exception as e:
            print(f"Error al cambiar estado a cancelado: {e}")
        
        return {
            'message': 'Rifa cancelada y reembolsos procesados exitosamente',
            'tickets_refunded': refunded_count,
            'total_amount_refunded': total_refunded,
            'admin_reason': admin_reason or 'No especificado',
            'cancellation_date': timezone.now(),
            'was_previously_drawn': bool(self.raffle_winner),
            'raffle_status': self.status_display
        }
    
    def soft_delete_and_refund(self, organizer_user):
        """
        Soft delete de la rifa por parte del organizador.
        Devuelve dinero a participantes y cancela la rifa.
        
        SOLO para uso del dueño/organizador de la rifa.
        """
        # Validar que el usuario sea el organizador
        if organizer_user != self.raffle_created_by:
            raise ValidationError("Solo el organizador puede cancelar la rifa")
        
        # No permitir cancelación si ya fue sorteada
        if self.raffle_winner:
            raise ValidationError("No se puede cancelar una rifa que ya fue sorteada")
        
        # Reembolsar todos los tickets
        tickets = self.sold_tickets.all()
        refunded_count = 0
        total_refunded = 0
        
        for ticket in tickets:
            # Devolver dinero al método de pago
            ticket.payment_method.add_balance(self.raffle_number_price)
            total_refunded += self.raffle_number_price
            refunded_count += 1
        
        # Eliminar todos los tickets
        tickets.delete()
        
        # Cambiar estado a cancelado
        from raffleInfo.models import StateRaffle
        try:
            cancelled_state = StateRaffle.objects.filter(
                state_raffle_code__iexact='CAN'
            ).first() or StateRaffle.objects.filter(
                state_raffle_name__icontains='cancel'
            ).first()
            
            if cancelled_state:
                self.raffle_state = cancelled_state
                self.save()
        except Exception as e:
            print(f"Error al cambiar estado a cancelado: {e}")
        
        return {
            'message': 'Rifa cancelada exitosamente por el organizador',
            'tickets_refunded': refunded_count,
            'total_amount_refunded': total_refunded,
            'organizer': organizer_user.email,
            'cancellation_date': timezone.now(),
            'cancellation_type': 'organizer_soft_delete'
        }
    
    @property
    def total_revenue(self): #Total recaudado por venta de tickets
        return Decimal(str(self.numbers_sold)) * self.raffle_number_price
    
    def can_execute_draw(self): #Verifica si se puede ejecutar el sorteo
        now = timezone.now()
        
        if self.raffle_winner:
            return False, "El sorteo ya fue ejecutado"
        
        if not self._is_in_active_state():
            return False, "La rifa no está activa"
        
        if now < self.raffle_draw_date:
            return False, f"El sorteo está programado para {self.raffle_draw_date}"
        
        if not self.minimum_reached:
            remaining = self.raffle_minimum_numbers_sold - self.numbers_sold
            return False, f"No se alcanzó el mínimo. Faltan {remaining} números por vender"
        
        return True, "Listo para sortear"
    
    def execute_raffle_draw(self): #Ejacuta el sorteo de la rifa

        can_draw, message = self.can_execute_draw() #Verificar si se puede ejecutar el sorteo
        if not can_draw:
            raise ValueError(message)
        
        import random #Se realiza el sorteo de forma aleatoria 
        sold_tickets = list(self.sold_tickets.all())
        
        if not sold_tickets:
            raise ValueError("No hay tickets vendidos para sortear")
        
        winner_ticket = random.choice(sold_tickets)
        
        winner_ticket.is_winner = True
        winner_ticket.save()
        
        self.raffle_winner = winner_ticket.user #Se actualiza el ganador de la rifa
        
        self._change_state_to_sorted() #Se cambia el estado de la rifa a sorteada
        
        self.save()
        
        total_sold = self.numbers_sold
        total_revenue = total_sold * self.raffle_number_price
        
        return { #Resultados del sorteo
            'message': f"¡Sorteo 100% aleatorio ejecutado exitosamente!",
            'winner_user': winner_ticket.user.email,
            'winner_number': winner_ticket.number,
            'winner_payment_method': str(winner_ticket.payment_method.payment_method_type),
            'prize_type': self.raffle_prize_type.prize_type_name,
            'prize_amount': str(self.raffle_prize_amount),
            'tickets_sold': total_sold,
            'total_revenue': str(total_revenue),
            'raffle_status': self.status_display,
        }
    
    def _change_state_to_sorted(self): #Cambia el estado de la rifa a sorteada

        try:
            sorted_state = StateRaffle.objects.filter(
                state_raffle_code__iexact='SOR'
            ).first() or StateRaffle.objects.filter(
                state_raffle_name__icontains='sortead'
            ).first()
            
            if sorted_state:
                self.raffle_state = sorted_state
            else:
                print("Warning: No se encontró estado 'Sorteado' disponible")
        except Exception as e:
            print(f"Error al cambiar estado después del sorteo: {e}")