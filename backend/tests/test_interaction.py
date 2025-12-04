import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from interactions.models import Interaction
from location.models import City, Country, State
from user.models import User
from userInfo.models import DocumentType, Gender


class InteractionAPITestCase(APITestCase):
    """
    Tests para el sistema de interacciones
    """

    @classmethod
    def setUpTestData(cls):
        """Crear datos comunes para todos los tests"""
        # Crear location
        cls.country = Country.objects.create(
            country_name="TestCountry", country_code="TC"
        )
        cls.state = State.objects.create(
            state_name="TestState", state_country=cls.country, state_code="TS"
        )
        cls.city = City.objects.create(
            city_name="TestCity", city_state=cls.state, city_code="TCY"
        )

        # Crear gender y document_type
        cls.gender = Gender.objects.create(gender_name="Non-Binary", gender_code="NB")
        cls.document_type = DocumentType.objects.create(
            document_type_name="Passport", document_type_code="PP"
        )

        # Crear usuarios de prueba
        cls.user1 = User.objects.create_user(
            email="user1@test.com",
            password="testpass123",
            first_name="User",
            last_name="One",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="11111111",
            city=cls.city,
        )

        cls.user2 = User.objects.create_user(
            email="user2@test.com",
            password="testpass123",
            first_name="User",
            last_name="Two",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="22222222",
            city=cls.city,
        )

        cls.user3 = User.objects.create_user(
            email="user3@test.com",
            password="testpass123",
            first_name="User",
            last_name="Three",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="33333333",
            city=cls.city,
        )

    def setUp(self):
        """Refrescar usuarios antes de cada test"""
        self.user1 = self.__class__.user1
        self.user2 = self.__class__.user2
        self.user3 = self.__class__.user3
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.user3.refresh_from_db()

    def test_list_interactions_anonymous(self):
        """Usuarios anónimos pueden ver interacciones"""
        url = reverse("interaction-list")
        Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_interaction_authenticated(self):
        """Usuario autenticado puede crear interacción"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("interaction-list")
        data = {
            "interaction_target_user": self.user2.id,
            "interaction_rating": 4.0,
            "interaction_comment": "Great user!",
        }

        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Interaction.objects.count() == 1

    def test_create_interaction_anonymous_fails(self):
        """Usuario anónimo no puede crear interacción"""
        url = reverse("interaction-list")
        data = {"interaction_target_user": self.user2.id, "interaction_rating": 4.0}

        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_create_duplicate_interaction(self):
        """No se puede crear interacción duplicada"""
        self.client.force_authenticate(user=self.user1)
        Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
        )

        url = reverse("interaction-list")
        data = {"interaction_target_user": self.user2.id, "interaction_rating": 5.0}

        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_own_interaction(self):
        """Usuario puede actualizar su propia interacción"""
        self.client.force_authenticate(user=self.user1)
        interaction = Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
        )

        url = reverse("interaction-detail", args=[interaction.pk])
        data = {"interaction_rating": 5.0}

        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Interaction.objects.get().interaction_rating == 5.0

    def test_cannot_update_others_interaction(self):
        """Usuario no puede actualizar interacción de otro"""
        self.client.force_authenticate(user=self.user2)
        interaction = Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
        )

        url = reverse("interaction-detail", args=[interaction.pk])
        data = {"interaction_rating": 1.0}

        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_interaction(self):
        """Usuario puede eliminar su propia interacción"""
        self.client.force_authenticate(user=self.user1)
        interaction = Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
        )

        url = reverse("interaction-detail", args=[interaction.pk])
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Interaction.objects.count() == 0

    def test_cannot_delete_others_interaction(self):
        """Usuario no puede eliminar interacción de otro"""
        self.client.force_authenticate(user=self.user2)
        interaction = Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
        )

        url = reverse("interaction-detail", args=[interaction.pk])
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Interaction.objects.count() == 1

    def test_get_user_rating(self):
        """Obtener promedio de calificaciones de un usuario"""
        self.client.force_authenticate(user=self.user1)

        # Crear interacciones desde diferentes usuarios
        Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
        )
        Interaction.objects.create(
            interaction_source_user=self.user3,
            interaction_target_user=self.user2,
            interaction_rating=5.0,
        )

        url = reverse("interaction-user-rating")
        response = self.client.get(f"{url}?user_id={self.user2.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_rating"], 4.5)
