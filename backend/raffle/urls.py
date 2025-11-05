from django.urls import path
from .views import RaffleCreateView

urlpatterns = [
    path('create/', RaffleCreateView.as_view(), name='raffle-create'),
]