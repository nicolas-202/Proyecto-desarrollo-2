from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from raffleInfo.models import PrizeType, StateRaffle
from user.models import User
import os

def raffle_image_upload_path(instance, filename):
    """
    Función para definir la ruta de subida de imágenes de rifas
    Estructura: media/raffles/{year}/{month}/{raffle_id}_{filename}
    """
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

# Create your models here.
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
        validators=[MinValueValidator(0.01)],
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
    raffle_price_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Monto del premio',
        help_text='Monto total del premio de la rifa'
    )
    raffle_prize_type = models.ForeignKey(
        PrizeType, 
        on_delete=models.RESTRICT,  # Cambié de CASCADE a RESTRICT para mayor seguridad
        verbose_name='Tipo de premio'
    )
    raffle_state = models.ForeignKey(
        StateRaffle, 
        on_delete=models.RESTRICT,  # Cambié de CASCADE a RESTRICT
        verbose_name='Estado de la rifa'
    )
    raffle_created_by = models.ForeignKey(
        User, 
        on_delete=models.RESTRICT,  # Cambié de CASCADE a RESTRICT
        related_name='created_raffles',
        verbose_name='Creado por'
    )
    
    # Campos de auditoría (recomendados)
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
        ]

    def clean(self):
        """Validaciones personalizadas"""
        errors = []
        
        # Validar que la fecha de sorteo sea posterior a la fecha de inicio
        if self.raffle_start_date and self.raffle_draw_date:
            if self.raffle_start_date >= self.raffle_draw_date:
                errors.append('La fecha de inicio debe ser anterior a la fecha del sorteo')
        
        # Validar que la fecha de sorteo no sea en el pasado (solo para actualizaciones)
        if self.pk and self.raffle_draw_date and self.raffle_draw_date < timezone.now():
            errors.append('La fecha del sorteo no puede ser en el pasado')
        
        # Validar que el mínimo de números sea menor o igual al total
        if (self.raffle_minimum_numbers_sold and 
            self.raffle_number_amount and 
            self.raffle_minimum_numbers_sold > self.raffle_number_amount):
            errors.append('El mínimo de números para sortear no puede ser mayor al total de números disponibles')
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Asignar estado por defecto "Activo" al crear nueva rifa
        if not self.pk and not self.raffle_state:  # Solo para nuevas rifas
            self._assign_default_active_state()
        
        self.clean()
        super().save(*args, **kwargs)
    
    def _assign_default_active_state(self):
        """
        Método privado para asignar estado activo por defecto
        """
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

    def _is_in_active_state(self):
        """
        Método para verificar si la rifa está en un estado activo
        """
        if not self.raffle_state:
            return False
        
        # Verificar por código de estado
        active_codes = ['ACT', 'ACTIVE', 'A']
        if self.raffle_state.state_raffle_code:
            if self.raffle_state.state_raffle_code.upper() in active_codes:
                return True
        
        # Verificar por nombre de estado (fallback)
        if self.raffle_state.state_raffle_name:
            active_keywords = ['activ', 'abierta', 'disponible', 'vigente']
            state_name_lower = self.raffle_state.state_raffle_name.lower()
            return any(keyword in state_name_lower for keyword in active_keywords)
        
        return False

    @property
    def image_url(self):
        """
        Retorna la URL de la imagen si existe, sino la imagen por defecto
        """
        if self.raffle_image:
            return self.raffle_image.url
        
        # Retornar imagen por defecto
        from django.conf import settings
        import os
        
        # Buscar imagen por defecto en diferentes formatos
        default_path_base = os.path.join(settings.MEDIA_ROOT, 'raffles', 'defaults', 'default_raffle')
        possible_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        for ext in possible_extensions:
            full_path = default_path_base + ext
            if os.path.exists(full_path):
                return f"{settings.MEDIA_URL}raffles/defaults/default_raffle{ext}"
        
        # Si no encuentra ninguna imagen, retornar None o una URL placeholder
        return None
    
    @property
    def has_custom_image(self):
        """
        Verifica si la rifa tiene una imagen personalizada
        """
        return bool(self.raffle_image)
    
    @property
    def has_image(self):
        """
        Verifica si la rifa tiene imagen (siempre True porque incluye la por defecto)
        """
        return True

    @property
    def total_potential_income(self):
        """Calcula el ingreso potencial total"""
        return self.raffle_number_amount * self.raffle_number_price

    @property
    def numbers_sold(self):
        """Cantidad de números vendidos (simulado por ahora)"""
        # TODO: Cuando implementes el modelo de boletos/números vendidos,
        # reemplaza esto con la consulta real
        # return self.raffle_tickets.filter(is_paid=True).count()
        return 0  # Por ahora retorna 0
    
    @property
    def numbers_available(self):
        """Cantidad de números disponibles"""
        return self.raffle_number_amount - self.numbers_sold
    
    @property
    def sales_progress_percentage(self):
        """Porcentaje de progreso de ventas"""
        if self.raffle_number_amount == 0:
            return 0
        return (self.numbers_sold / self.raffle_number_amount) * 100
    
    @property
    def minimum_reached(self):
        """Verifica si se alcanzó el mínimo de números vendidos"""
        return self.numbers_sold >= self.raffle_minimum_numbers_sold
    
    @property
    def is_active_for_sales(self):
        """Verifica si la rifa está activa para ventas"""
        now = timezone.now()
        return (
            self._is_in_active_state() and
            self.raffle_start_date <= now < self.raffle_draw_date and
            self.numbers_available > 0 and
            not self.raffle_winner  # No ha sido sorteada
        )
    
    @property
    def is_ready_for_draw(self):
        """Verifica si la rifa está lista para ser sorteada"""
        now = timezone.now()
        return (
            self._is_in_active_state() and
            now >= self.raffle_draw_date and
            self.minimum_reached and
            not self.raffle_winner  # No ha sido sorteada aún
        )
    
    @property
    def can_be_drawn(self):
        """Verifica si la rifa puede ser sorteada (sin importar la fecha)"""
        return (
            self._is_in_active_state() and
            self.minimum_reached and
            not self.raffle_winner
        )
    
    @property
    def time_until_draw(self):
        """Retorna el tiempo restante hasta el sorteo"""
        if self.raffle_draw_date:
            return self.raffle_draw_date - timezone.now()
        return None
    
    @property
    def status_display(self):
        """Retorna una descripción amigable del estado actual"""
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

    def __str__(self):
        return self.raffle_name
    
    def can_execute_draw(self):
        """
        Verifica si se puede ejecutar el sorteo y retorna el resultado
        """
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
        
        if self.numbers_sold == 0:
            return False, "No hay números vendidos para sortear"
        
        return True, "Listo para sortear"
    
    def execute_raffle_draw(self, winner_user=None):
        """
        Ejecuta el sorteo de la rifa y cambia automáticamente el estado a inactivo
        """
        from raffleInfo.models import StateRaffle
        
        # Verificar si se puede ejecutar el sorteo
        can_draw, message = self.can_execute_draw()
        if not can_draw:
            raise ValueError(message)
        
        # Asignar ganador
        if winner_user:
            self.raffle_winner = winner_user
        
        # Cambiar estado a inactivo automáticamente
        try:
            inactive_state = StateRaffle.objects.filter(
                state_raffle_code__iexact='INA'  # Asumiendo 'INA' para Inactivo
            ).first()
            
            if not inactive_state:
                # Buscar por nombre si no encuentra por código
                inactive_state = StateRaffle.objects.filter(
                    state_raffle_name__icontains='inactiv'
                ).first()
            
            if inactive_state:
                self.raffle_state = inactive_state
                print(f"Estado cambiado a: {inactive_state.state_raffle_name}")
            else:
                print("Warning: No se encontró estado 'Inactivo' para asignar después del sorteo")
                
        except Exception as e:
            print(f"Error al cambiar estado después del sorteo: {e}")
        
        # Guardar cambios
        self.save()
        
        return f"Sorteo ejecutado exitosamente. Ganador: {self.raffle_winner}"
    
    def mark_as_inactive(self):
        """
        Marca la rifa como inactiva manualmente
        """
        from raffleInfo.models import StateRaffle
        
        try:
            inactive_state = StateRaffle.objects.filter(
                state_raffle_code__iexact='INA'
            ).first()
            
            if not inactive_state:
                inactive_state = StateRaffle.objects.filter(
                    state_raffle_name__icontains='inactiv'
                ).first()
            
            if inactive_state:
                self.raffle_state = inactive_state
                self.save()
                return f"Rifa marcada como {inactive_state.state_raffle_name}"
            else:
                return "Error: No se encontró estado inactivo"
                
        except Exception as e:
            return f"Error al marcar como inactiva: {e}"