# backend/raffle/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender='raffle.Raffle')
def auto_process_expired_raffle(sender, instance, created, **kwargs):
    """
    Procesar rifa automáticamente si pasó su fecha.
    Se ejecuta cada vez que se guarda una rifa (creación o actualización).
    """
    # Evitar procesamiento en creación inicial o si ya tiene ganador
    if created or instance.raffle_winner:
        return
    
    now = timezone.now()
    
    # Solo procesar si la rifa pasó su fecha de sorteo
    if (instance.raffle_draw_date <= now and 
        not instance.raffle_winner and 
        instance._is_in_active_state()):
        
        logger.info(f"Procesando rifa vencida: {instance.id} - {instance.raffle_name}")
        
        if instance.minimum_reached:
            try:
                # Ejecutar sorteo automáticamente
                result = instance.execute_raffle_draw()
                logger.info(f"✅ Sorteo automático exitoso para rifa {instance.id}: {result.get('winner_user', 'N/A')}")
            except Exception as e:
                logger.error(f"❌ Error auto-sorteo rifa {instance.id}: {e}")
        else:
            try:
                # Auto-cancelar si no alcanzó mínimo CON REEMBOLSOS
                from raffleInfo.models import StateRaffle
                cancelled_state = StateRaffle.objects.filter(
                    state_raffle_code__iexact='CAN'
                ).first() or StateRaffle.objects.filter(
                    state_raffle_name__icontains='cancel'
                ).first()
                
                if cancelled_state and instance.raffle_state != cancelled_state:
                    # Usar método de cancelación con reembolsos
                    result = instance.cancel_raffle_and_refund(
                        admin_reason="Cancelación automática: mínimo no alcanzado"
                    )
                    
                    logger.info(
                        f"📋 Rifa {instance.id} cancelada automáticamente con reembolsos - "
                        f"Tickets reembolsados: {result['tickets_refunded']}, "
                        f"Monto total: ${result['total_amount_refunded']}"
                    )
                else:
                    logger.warning(f"⚠️ No se encontró estado cancelado o la rifa {instance.id} ya está cancelada")
                
            except Exception as e:
                logger.error(f"❌ Error auto-cancelación con reembolsos rifa {instance.id}: {e}")


# Signal adicional para verificar rifas cuando se consultan
from django.db.models.signals import post_init

@receiver(post_init, sender='raffle.Raffle')
def check_raffle_on_load(sender, instance, **kwargs):
    """
    Verificar y procesar rifa cuando se carga desde la base de datos.
    Útil para casos donde la rifa no se ha actualizado en mucho tiempo.
    """
    if not instance.pk:  # Solo para instancias existentes
        return
        
    now = timezone.now()
    
    # Solo verificar si la rifa pasó su fecha hace más de 1 hora (para evitar spam)
    if (instance.raffle_draw_date <= now and 
        not instance.raffle_winner and 
        instance._is_in_active_state() and
        (now - instance.raffle_draw_date).total_seconds() > 3600):  # 1 hora
        
        # Trigger un save para activar el signal de post_save
        try:
            instance._allow_past_date = True  # Permitir guardar con fecha pasada
            instance.save()
        except Exception as e:
            logger.error(f"Error al procesar rifa en carga: {e}")