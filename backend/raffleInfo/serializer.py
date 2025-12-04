from rest_framework import serializers

from .models import PrizeType, StateRaffle


class PrizeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrizeType
        fields = "__all__"


class StateRaffleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateRaffle
        fields = "__all__"
