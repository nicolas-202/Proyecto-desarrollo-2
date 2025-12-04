from django.db.models import Avg
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from permissions.permissions import IsOwnerOrReadOnly

from .models import Interaction
from .serializer import InteractionSerializer


class InteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de interacciones.
    """

    queryset = Interaction.objects.filter(Interaction_is_active=True)
    serializer_class = InteractionSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Personaliza el queryset base para incluir filtros
        """
        queryset = super().get_queryset()

        # Filtrar por usuario objetivo si se proporciona
        target_user = self.request.query_params.get("target_user", None)
        if target_user:
            queryset = queryset.filter(interaction_target_user_id=target_user)

        # Filtrar por usuario fuente si se proporciona
        source_user = self.request.query_params.get("source_user", None)
        if source_user:
            queryset = queryset.filter(interaction_source_user_id=source_user)

        return queryset

    @action(detail=False, methods=["GET"])
    def user_rating(self, request):
        """
        Obtiene el promedio de calificaciones de un usuario
        GET /api/interactions/user_rating/?user_id=<id>
        """
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"error": "Se requiere el parámetro user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = (
            self.get_queryset()
            .filter(interaction_target_user_id=user_id)
            .aggregate(avg_rating=Avg("interaction_rating"))
        )

        return Response(
            {"user_id": user_id, "average_rating": rating["avg_rating"] or 0}
        )

    def perform_create(self, serializer):
        """
        Asigna el usuario actual como fuente de la interacción
        """
        serializer.save(interaction_source_user=self.request.user)
