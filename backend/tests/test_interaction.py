from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from interactions.models import Interaction
from django.core.exceptions import ValidationError
from location.models import Country, State, City
from user.models import User
from userInfo.models import Gender, DocumentType

User = get_user_model()

class InteractionTest(APITestCase):

    @classmethod    
    def setUpTestData(cls):
        """Crear datos comunes para todos los tests"""
        # Crear location
        cls.country = Country.objects.create(
            country_name="TestCountry",
            country_code="TC"
        )
        cls.state = State.objects.create(
            state_name="TestState",
            state_country=cls.country,
            state_code="TS"
        )
        cls.city = City.objects.create(
            city_name="TestCity",
            city_state=cls.state,
            city_code="TCY"
        )
        
        # Crear otro city para tests de actualización
        cls.other_city = City.objects.create(
            city_name="OtherCity",
            city_state=cls.state,
            city_code="OCY"
        )

        # Crear gender y document_type
        cls.gender = Gender.objects.create(
            gender_name="Non-Binary",
            gender_code="NB"
        )
        cls.other_gender = Gender.objects.create(
            gender_name="Female",
            gender_code="F"
        )
        cls.document_type = DocumentType.objects.create(
            document_type_name="Passport",
            document_type_code="PP"
        )

        cls.user1 = User.objects.create_user(email='user1@example.com', password='password123', city = cls.city, gender = cls.gender, document_type = cls.document_type, first_name= 'user', last_name='user', document_number=12345678)
        cls.user2 = User.objects.create_user(email='user2@example.com', password='password123', city = cls.city, gender = cls.gender, document_type = cls.document_type, first_name= 'user', last_name='user', document_number=12345679)
        cls.user3 = User.objects.create_user(email='user3@example.com', password='password123', city = cls.city, gender = cls.gender, document_type = cls.document_type, first_name= 'user', last_name='user', document_number=12345670)
    def setUp(self):
        """Refrescar usuarios antes de cada test"""
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.user3.refresh_from_db()
    
    def test_create_interaction_updates_rating(self):
        # Crear interacción: user1 califica a user2 con 4.0
        Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
            Interaction_is_active=True
        )
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.rating, 4.0)

        # Crear otra interacción: user3 califica a user2 con 5.0
        Interaction.objects.create(
            interaction_source_user=self.user3,
            interaction_target_user=self.user2,
            interaction_rating=5.0,
            Interaction_is_active=True
        )
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.rating, 4.5)  # Promedio: (4.0 + 5.0) / 2

    def test_update_interaction_updates_rating(self):
        interaction = Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=3.0,
            Interaction_is_active=True
        )
        # Actualizar rating a 4.0
        interaction.interaction_rating = 4.0
        interaction.save()
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.rating, 4.0)

    def test_delete_interaction_updates_rating(self):
        Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
            Interaction_is_active=True
        )
        Interaction.objects.create(
            interaction_source_user=self.user3,
            interaction_target_user=self.user2,
            interaction_rating=5.0,
            Interaction_is_active=True
        )
        # Eliminar una interacción
        Interaction.objects.filter(interaction_source_user=self.user1).delete()
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.rating, 5.0)  # Solo queda la calificación de 5.0

    def test_soft_delete_interaction_updates_rating(self):
        interaction = Interaction.objects.create(
            interaction_source_user=self.user1,
            interaction_target_user=self.user2,
            interaction_rating=4.0,
            Interaction_is_active=True
        )
        # Soft-delete: Interaction_is_active = False
        interaction.Interaction_is_active = False
        interaction.save()
        self.user2.refresh_from_db()
        self.assertIsNone(self.user2.rating)  # Sin interacciones activas

    def test_no_interactions_sets_rating_null(self):
        self.assertIsNone(self.user2.rating)  # Sin interacciones, rating es None