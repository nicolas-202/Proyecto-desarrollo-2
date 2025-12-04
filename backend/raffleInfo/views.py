# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets

from permissions.permissions import IsAdminOrReadOnly

from .models import PrizeType, StateRaffle
from .serializer import PrizeTypeSerializer, StateRaffleSerializer


class BaseraflleinfoViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        # Aplicar IsAdminOrReadOnly para todas las acciones
        return [IsAdminOrReadOnly()]


class PrizeTypeViewSet(BaseraflleinfoViewSet):
    serializer_class = PrizeTypeSerializer
    queryset = PrizeType.objects.all()


class StateRaffleViewSet(BaseraflleinfoViewSet):
    serializer_class = StateRaffleSerializer
    queryset = StateRaffle.objects.all()
