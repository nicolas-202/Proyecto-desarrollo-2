from django.urls import path

from .views import (
    AdminRaffleCancelView,
    AvailableNumbersView,
    RaffleCreateView,
    RaffleDetailView,
    RaffleDrawView,
    RaffleListView,
    RaffleSoftDeleteView,
    RaffleUpdateView,
    RaffleUserListView,
)

urlpatterns = [
    # CRUD básico
    path("create/", RaffleCreateView.as_view(), name="raffle-create"),  # POST - Crear
    path(
        "list/", RaffleListView.as_view(), name="raffle-list"
    ),  # GET - Listar todas (públicas activas)
    path(
        "<int:pk>/", RaffleDetailView.as_view(), name="raffle-detail"
    ),  # GET - Detalle individual
    path(
        "<int:pk>/update/", RaffleUpdateView.as_view(), name="raffle-update"
    ),  # PUT/PATCH - Actualizar
    path(
        "<int:pk>/delete/", RaffleSoftDeleteView.as_view(), name="raffle-delete"
    ),  # PATCH - Soft delete (con reembolsos)
    path(
        "<int:pk>/admin-cancel/",
        AdminRaffleCancelView.as_view(),
        name="admin-raffle-cancel",
    ),  # PATCH - Cancelación administrativa
    path(
        "<int:pk>/draw/", RaffleDrawView.as_view(), name="raffle-draw"
    ),  # PATCH - Ejecutar sorteo
    path(
        "<int:pk>/available/", AvailableNumbersView.as_view(), name="available-numbers"
    ),  # GET - Números disponibles
    path(
        "user/<int:user_id>/", RaffleUserListView.as_view(), name="user-raffles"
    ),  # GET - Rifas de usuario (público)
]
