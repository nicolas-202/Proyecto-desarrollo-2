from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import User

class Interaction(models.Model):
    interaction_target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target_interactions')
    interaction_source_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='source_interactions')
    interaction_rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    interaction_comment = models.TextField(blank=True, null=True, max_length=500)
    interaction_created_at = models.DateTimeField(auto_now=True)
    Interaction_is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Interacción'
        verbose_name_plural = 'Interacciones'
        ordering = ['-interaction_created_at']  # Más recientes primero
        
        # Constraint: Un usuario solo puede calificar a otro usuario UNA vez
        constraints = [
            models.UniqueConstraint(
                fields=['interaction_source_user', 'interaction_target_user'],
                name='unique_interaction_per_user_pair'
            ),
            # Constraint: Un usuario no puede calificarse a sí mismo
            models.CheckConstraint(
                condition=~models.Q(interaction_source_user=models.F('interaction_target_user')),
                name='cannot_rate_self'
            )
        ]
        
        # Índices para mejorar consultas
        indexes = [
            models.Index(fields=['interaction_target_user', '-interaction_created_at']),
            models.Index(fields=['interaction_source_user', '-interaction_created_at']),
            models.Index(fields=['interaction_rating']),
        ]
    
    def __str__(self):
        return f"{self.interaction_source_user.email} → {self.interaction_target_user.email} ({self.interaction_rating}★)"
    
    def clean(self):
        """
        Validación adicional: un usuario no puede calificarse a sí mismo
        """
        from django.core.exceptions import ValidationError
        
        if self.interaction_source_user == self.interaction_target_user:
            raise ValidationError('Un usuario no puede calificarse a sí mismo.')
    
    def save(self, *args, **kwargs):
        """
        Validar antes de guardar
        """
        self.clean()
        super().save(*args, **kwargs)