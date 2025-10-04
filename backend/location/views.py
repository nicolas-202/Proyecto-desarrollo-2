from django.shortcuts import render
from rest_framework import viewsets
from .serializer import CountrySerializer
from .models import Country
# Create your views here.
class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()