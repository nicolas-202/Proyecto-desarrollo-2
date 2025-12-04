from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from user.models import User


class Interaction(models.Model):
    interaction_target_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="target_interactions"
    )
    interaction_source_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="source_interactions"
    )
    interaction_rating = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    interaction_comment = models.TextField(blank=True, null=True, max_length=500)
    interaction_created_at = models.DateTimeField(auto_now=True)
    Interaction_is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Interacción"
        verbose_name_plural = "Interacciones"
        ordering = ["-interaction_created_at"]

        # Constraint: Un usuario solo puede calificar a otro usuario UNA vez
        constraints = [
            models.UniqueConstraint(
                fields=["interaction_source_user", "interaction_target_user"],
                condition=models.Q(Interaction_is_active=True),
                name="unique_active_interaction",
            )
        ]

        # Índices para mejorar consultas
        indexes = [
            models.Index(fields=["interaction_target_user", "-interaction_created_at"]),
            models.Index(fields=["interaction_source_user", "-interaction_created_at"]),
            models.Index(fields=["interaction_rating"]),
        ]

    def __str__(self):
        return f"{self.interaction_source_user.email} → {self.interaction_target_user.email} ({self.interaction_rating}★)"

    def clean(self):
        """
        Validar que no exista una calificación activa previa
        """
        if not self.pk:  # Solo para nuevas interacciones
            existing_interaction = Interaction.objects.filter(
                interaction_source_user=self.interaction_source_user,
                interaction_target_user=self.interaction_target_user,
                Interaction_is_active=True,
            ).exists()

            if existing_interaction:
                raise ValidationError(
                    "Ya has calificado a este usuario. Debes desactivar la calificación anterior antes de crear una nueva."
                )

    def save(self, *args, **kwargs):
        """
        Validar antes de guardar
        """
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def can_rate(cls, source_user, target_user):
        """
        Verifica si un usuario puede calificar a otro
        """
        return not cls.objects.filter(
            interaction_source_user=source_user,
            interaction_target_user=target_user,
            Interaction_is_active=True,
        ).exists()
