from django.urls import path

from .views import (
    RaffleTicketsView,
    TicketListView,
    TicketPurchaseView,
    TicketRefundView,
    UserTicketHistoryView,
    UserTicketStatsView,
)

urlpatterns = [
    # Funcionalidad principal de tickets
    path(
        "purchase/", TicketPurchaseView.as_view(), name="ticket-purchase"
    ),  # POST - Comprar ticket
    path(
        "my-tickets/", TicketListView.as_view(), name="my-tickets"
    ),  # GET - Mis tickets
    path(
        "<int:pk>/refund/", TicketRefundView.as_view(), name="ticket-refund"
    ),  # PATCH - Reembolsar ticket
    # Información sobre rifas y tickets
    path(
        "raffle/<int:raffle_id>/", RaffleTicketsView.as_view(), name="raffle-tickets"
    ),  # GET - Tickets de una rifa
    # Estadísticas del usuario
    path(
        "stats/", UserTicketStatsView.as_view(), name="user-stats"
    ),  # GET - Estadísticas del usuario
    path(
        "user/<int:user_id>/history/",
        UserTicketHistoryView.as_view(),
        name="user-ticket-history",
    ),  # GET - Historial de un usuario
]
