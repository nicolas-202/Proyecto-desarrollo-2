from django.shortcuts import render
from rest_framework import viewsets
from .serializer import PaisSerializer
from .models import Pais
# Create your views here.
class PaisViewSet(viewsets.ModelViewSet):
    serializer_class = PaisSerializer
    queryset = Pais.objects.all()