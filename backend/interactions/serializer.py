from rest_framework import serializers
from .models import Interaction

class InteractionSerializer(serializers.ModelSerializer):
    # Campo calculado para verificar si se puede calificar
    can_rate = serializers.SerializerMethodField()

    class Meta:
        model = Interaction
        fields = (
            'id',
            'interaction_target_user',
            'interaction_source_user',
            'interaction_rating',
            'interaction_comment',
            'interaction_created_at',
            'Interaction_is_active',
            'can_rate'
        )
        read_only_fields = (
            'interaction_created_at',
            'interaction_source_user',
            'can_rate'
        )

    def get_can_rate(self, obj):
        """
        Verifica si el usuario actual puede calificar al usuario objetivo
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Interaction.can_rate(request.user, obj.interaction_target_user)

    def validate(self, data):
        """
        Validaciones personalizadas
        """
        target_user = data.get('interaction_target_user')
        source_user = self.context['request'].user

        if not Interaction.can_rate(source_user, target_user):
            raise serializers.ValidationError(
                "Ya has calificado a este usuario. Debes desactivar la calificación anterior."
            )

        data['interaction_source_user'] = source_user
        return data

    def validate_interaction_rating(self, value):
        """
        Validar que la calificación esté entre 1 y 5
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError(
                "La calificación debe estar entre 1 y 5 estrellas."
            )
        return value



