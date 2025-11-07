from django.urls import path
from .views import (
    RaffleCreateView, 
    RaffleListView, 
    RaffleSoftDeleteView,
    RaffleDetailView,
    RaffleUpdateView,
    RaffleMyListView,
    RaffleUserListView
)

urlpatterns = [
    # CRUD básico
    path('create/', RaffleCreateView.as_view(), name='raffle-create'),              # POST - Crear
    path('list/', RaffleListView.as_view(), name='raffle-list'),                   # GET - Listar todas (públicas activas)
    path('<int:pk>/', RaffleDetailView.as_view(), name='raffle-detail'),          # GET - Detalle individual
    path('<int:pk>/update/', RaffleUpdateView.as_view(), name='raffle-update'),   # PUT/PATCH - Actualizar
    path('<int:pk>/delete/', RaffleSoftDeleteView.as_view(), name='raffle-delete'), # PATCH - Soft delete
    
    # Endpoints por usuario
    path('my-raffles/', RaffleMyListView.as_view(), name='my-raffles'),           # GET - Mis rifas (auth)
    path('user/<int:user_id>/', RaffleUserListView.as_view(), name='user-raffles'), # GET - Rifas de usuario (público)
]