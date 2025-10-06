from django.shortcuts import render
from rest_framework import viewsets
from .serializer import CountrySerializer, StateSerializer, CitySerializer
from .models import Country, State, City


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

class StateViewSet(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()
    def get_queryset(self):
        queryset = super().get_queryset()
        state_id = self.request.query_params.get('country')
        if country_id:
            try:
                Country.objects.get(id=country_id)
                # Filter by state_country (ForeignKey field)
                queryset = queryset.filter(stat_country_id=country_id)
            except ValueError:
                raise ValidationError({"state": "Invalid country ID"})
        return queryset

class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        state_id = self.request.query_params.get('state')
        if state_id:
            try:
                State.objects.get(id=state_id)
                # Filter by city_state (ForeignKey field)
                queryset = queryset.filter(city_state_id=state_id)
            except ValueError:
                raise ValidationError({"state": "Invalid state ID"})
        return queryset