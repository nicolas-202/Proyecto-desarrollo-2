from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Interaction
from user.models import User

@receiver(post_save, sender=Interaction)
def update_user_rating_on_save(sender, instance, **kwargs):
    """
    Actualiza el campo rating del usuario objetivo cuando se crea o modifica una interacción.
    """
    target_user = instance.interaction_target_user
    # Calcular el promedio de calificaciones activas para el usuario objetivo
    avg_rating = Interaction.objects.filter(
        interaction_target_user=target_user,
        Interaction_is_active=True
    ).aggregate(Avg('interaction_rating'))['interaction_rating__avg']
    
    # Actualizar el campo rating (puede ser None si no hay calificaciones activas)
    target_user.rating = avg_rating
    target_user.save()

@receiver(post_delete, sender=Interaction)
def update_user_rating_on_delete(sender, instance, **kwargs):
    """
    Actualiza el campo rating del usuario objetivo cuando se elimina una interacción.
    """
    target_user = instance.interaction_target_user
    # Calcular el promedio de calificaciones activas para el usuario objetivo
    avg_rating = Interaction.objects.filter(
        interaction_target_user=target_user,
        Interaction_is_active=True
    ).aggregate(Avg('interaction_rating'))['interaction_rating__avg']
    
    # Actualizar el campo rating (puede ser None si no hay calificaciones activas)
    target_user.rating = avg_rating
    target_user.save()