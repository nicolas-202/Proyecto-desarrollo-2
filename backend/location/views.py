from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializer import CountrySerializer
from .serializer import StateSerializer
from .models import Country
from .models import State

# Create your views here.
class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

class StateViewSet(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()


    @action(detail=False, methods=['get'], url_path='by-country/(?P<country_id>[^/.]+)')
    def by_country(self, request, country_id=None):
        states = State.objects.filter(state_country_id=country_id)
        serializer = self.get_serializer(states, many=True)
        return Response(serializer.data)