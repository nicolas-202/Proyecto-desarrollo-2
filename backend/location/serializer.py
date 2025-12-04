from rest_framework import serializers

from .models import City, Country, State


class CountryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "country_name")


class StateMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ("id", "state_name")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            "id",
            "country_name",
            "country_code",
            "country_description",
            "country_is_active",
        )

    def validate_country_name(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                "El nombre del país no puede exceder 50 caracteres."
            )
        return value

    def validate_country_code(self, value):
        if not (2 <= len(value) <= 4 and value.isalnum()):
            raise serializers.ValidationError(
                "El código del país debe tener entre 2 y 4 caracteres alfanuméricos."
            )
        return value

    def validate_country_description(self, value):
        if value and len(value) > 200:
            raise serializers.ValidationError(
                "La descripción del país no puede exceder 200 caracteres."
            )
        return value


class StateSerializer(serializers.ModelSerializer):
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), source="state_country", write_only=True
    )
    state_country = CountryMinimalSerializer(read_only=True)

    class Meta:
        model = State
        fields = (
            "id",
            "state_name",
            "state_code",
            "state_description",
            "state_is_active",
            "country_id",
            "state_country",
        )

    def validate_state_name(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                "El nombre del estado no puede exceder 50 caracteres."
            )
        return value

    def validate_state_code(self, value):
        if not (2 <= len(value) <= 4 and value.isalnum()):
            raise serializers.ValidationError(
                "El código del estado debe tener entre 2 y 4 caracteres alfanuméricos."
            )
        return value

    def validate_state_description(self, value):
        if value and len(value) > 200:
            raise serializers.ValidationError(
                "La descripción del estado no puede exceder 200 caracteres."
            )
        return value

    def validate(self, data):
        name = data.get("state_name")
        country = data.get("state_country")
        if (
            name
            and country
            and State.objects.filter(state_name=name, state_country=country)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                "El nombre del estado ya existe para este país."
            )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["state_country"] = CountryMinimalSerializer(
            instance.state_country
        ).data
        return representation


class CitySerializer(serializers.ModelSerializer):
    state_id = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.all(), source="city_state", write_only=True
    )
    city_state = StateMinimalSerializer(read_only=True)

    class Meta:
        model = City
        fields = (
            "id",
            "city_name",
            "city_code",
            "city_description",
            "city_is_active",
            "state_id",
            "city_state",
        )

    def validate_city_name(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                "El nombre de la ciudad no puede exceder 50 caracteres."
            )
        return value

    def validate_city_code(self, value):
        if not (2 <= len(value) <= 4 and value.isalnum()):
            raise serializers.ValidationError(
                "El código de la ciudad debe tener entre 2 y 4 caracteres alfanuméricos."
            )
        return value

    def validate_city_description(self, value):
        if value and len(value) > 200:
            raise serializers.ValidationError(
                "La descripción de la ciudad no puede exceder 200 caracteres."
            )
        return value

    def validate(self, data):
        name = data.get("city_name")
        state = data.get("city_state")
        if (
            name
            and state
            and City.objects.filter(city_name=name, city_state=state)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                "El nombre de la ciudad ya existe para este estado."
            )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["city_state"] = StateMinimalSerializer(instance.city_state).data
        return representation
