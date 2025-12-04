from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from location.models import City
from location.serializer import CitySerializer
from userInfo.serializer import DocumentTypeSerializer, GenderSerializer

from .models import User


# Serializador para el registro de usuarios
class RegisterUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "city",
            "gender",
            "document_type",
            "document_number",
            "phone_number",
            "address",
        )
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def validate(self, data):
        # Validar que las contraseñas coincidan
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        if password != confirm_password:
            raise serializers.ValidationError("Las contraseñas no coinciden.")

        # Verificar si el email pertenece a un usuario inactivo
        email = data.get("email")
        if email and User.objects.filter(email=email, is_active=False).exists():
            raise serializers.ValidationError(
                "Esta cuenta está desactivada. Por favor, contacta al soporte para reactivar tu cuenta."
            )

        # Verificar si el documento pertenece a un usuario inactivo
        document_number = data.get("document_number")
        if (
            document_number
            and User.objects.filter(
                document_number=document_number, is_active=False
            ).exists()
        ):
            raise serializers.ValidationError(
                "Este número de documento pertenece a una cuenta desactivada. Por favor, contacta al soporte para reactivar tu cuenta."
            )

        return data

    def validate_phone_number(self, value):
        if value:
            if len(value) != 10:
                raise serializers.ValidationError(
                    "El número de teléfono debe tener 10 dígitos."
                )
            if not value.isdigit():
                raise serializers.ValidationError(
                    "El número de teléfono solo puede contener dígitos."
                )
        return value

    def validate_document_number(self, value):
        # Verificar que sea numérico
        if not str(value).isdigit():
            raise serializers.ValidationError(
                "El número de documento debe ser un valor numérico."
            )

        # Verificar que no esté en uso
        if User.objects.filter(document_number=value).exists():
            raise serializers.ValidationError("El número de documento ya está en uso.")

        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo electrónico ya está en uso.")
        return value

    def create(self, validated_data):
        # Eliminar confirm_password de validated_data
        validated_data.pop("confirm_password", None)
        # Extraer password y crear el usuario
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["city"] = CitySerializer(instance.city).data
        representation["gender"] = GenderSerializer(instance.gender).data
        representation["document_type"] = DocumentTypeSerializer(
            instance.document_type
        ).data
        representation["full_name"] = instance.get_full_name()
        return representation


class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "rating",
        )


# Serializador para mostrar información del perfil de usuario
class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "city",
            "gender",
            "document_type",
            "document_number",
            "phone_number",
            "address",
            "rating",
        )
        read_only_fields = ("id", "email", "document_type", "document_number")

    def get_full_name(self, obj):
        return obj.get_full_name()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["city"] = CitySerializer(instance.city).data
        representation["gender"] = GenderSerializer(instance.gender).data
        representation["document_type"] = DocumentTypeSerializer(
            instance.document_type
        ).data

        return representation


# Serializador para actualizar información del perfil de usuario
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "city",
            "gender",
        )

    def validate_phone_number(self, value):
        if value and len(value) != 10:
            raise serializers.ValidationError(
                "El número de teléfono debe tener 10 digitos."
            )
        return value


# Serializador para que el admin pueda actualizar usuarios, tambien es usado para listar usuarios
class AdminUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "is_active",
            "is_admin",
            "document_number",
            "document_type",
        )
        # Se pueden modificar document_type y document_number, pues el admin puede corregir errores de ingreso

        read_only_fields = ("id", "email", "full_name")

    def get_full_name(self, obj):
        return obj.get_full_name()

    def validate(self, data):
        request = self.context.get("request")
        current_user = request.user if request else None
        instance = self.instance

        is_admin = data.get("is_admin", instance.is_admin if instance else False)
        if not is_admin and instance:
            active_admins = User.objects.filter(is_admin=True).exclude(id=instance.id)
            if not active_admins.exists():
                raise serializers.ValidationError(
                    f"No se puede desactivar el último administrador (ID: {instance.id})."
                )

        is_active = data.get("is_active", instance.is_active if instance else True)
        if (
            not is_active
            and instance
            and current_user
            and instance.id == current_user.id
        ):
            raise serializers.ValidationError("No puedes desactivarte a ti mismo.")

        return data


# Serializador para cambiar la contraseña
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(
        required=True, write_only=True, min_length=8
    )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError(
                "La nueva contraseña no puede ser igual a la contraseña actual."
            )
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class DeleteAccountSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

        return data

    def save(self):
        user = self.context["request"].user
        user.is_active = False
        user.save()
        return user


# Serializador personalizado para login con JWT
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para login con JWT
    Devuelve tokens + información del usuario
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["is_staff"] = user.is_staff
        token["is_admin"] = user.is_admin
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "is_staff": self.user.is_staff,
            "is_admin": self.user.is_admin,
            "groups": [group.name for group in self.user.groups.all()],
        }
        return data
