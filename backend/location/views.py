from django.shortcuts import render
from rest_framework import viewsets
from .serializer import CountrySerializer, StateSerializer, CitySerializer
from .models import Country, State, City
from rest_framework.exceptions import ValidationError


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

class StateViewSet(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        country_id = self.request.query_params.get('country')
        if country_id:
            try:
                # Intentar convertir a entero
                int(country_id)
                Country.objects.get(id=country_id)
                queryset = queryset.filter(state_country_id=country_id)
            except ValueError:
                # ID no es numérico
                raise ValidationError({"country": "Invalid country ID format"})
            except Country.DoesNotExist:
                # País no existe
                raise ValidationError({"country": "Country not found"})
        return queryset

class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        state_id = self.request.query_params.get('state')
        if state_id:
            try:
                # Intentar convertir a entero
                int(state_id)
                State.objects.get(id=state_id)
                queryset = queryset.filter(city_state_id=state_id)
            except ValueError:
                # ID no es numérico
                raise ValidationError({"state": "Invalid state ID format"})
            except Country.DoesNotExist:
                # País no existe
                raise ValidationError({"state": "State not found"})
        return queryset