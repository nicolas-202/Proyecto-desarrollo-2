from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets
from .serializer import  PrizeTypeSerializer, StateRaffleSerializer
from .models import prizetype
from .models import  staterife
from permissions.permissions import IsAdminOrReadOnly

class BaseraflleinfoViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        # Aplicar IsAdminOrReadOnly para todas las acciones
        return [IsAdminOrReadOnly()]


class PrizeTypeViewSet(BaseraflleinfoViewSet):
    serializer_class = PrizeTypeSerializer
    queryset = prizetype.objects.all()


class StateRaffleViewSet(BaseraflleinfoViewSet):
    serializer_class = StateRaffleSerializer
    queryset = staterife.objects.all()




