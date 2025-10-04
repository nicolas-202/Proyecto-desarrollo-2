from rest_framework import serializers
from .models import Country, State


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='state_country.pais_name')
    class Meta:
        model = State
        fields = '__all__'