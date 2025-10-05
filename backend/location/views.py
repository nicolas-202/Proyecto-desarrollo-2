from django.shortcuts import render
from rest_framework import viewsets
from .serializer import CountrySerializer
from .serializer import StateSerializer
from .models import Country
from .models import State

class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

class StateViewSet(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()