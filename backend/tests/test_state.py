# location/tests/test_state.py
from rest_framework import status

from location.models import Country, State
from tests.base_test import BaseApiTest


class StateViewSetTestCase(BaseApiTest):
    __test__ = True  # Indica a pytest que esta clase debe ser probada.
    """Tests para StateViewSet"""

    url_list_name = "state-list"
    url_detail_name = "state-detail"
    model_class = State

    @classmethod
    def setUpTestData(cls):
        """
        Crear dependencias extras (Country) antes de ejecutar setUp base
        """
        super().setUpTestData()

        cls.test_country = Country.objects.create(
            country_name="Colombia for States",
            country_code="COS",
            country_description="País para estados de prueba",
            country_is_active=True,
        )

        cls.other_country = Country.objects.create(
            country_name="Venezuela for States",
            country_code="VES",
            country_description="Otro país",
            country_is_active=True,
        )

    def create_test_object(self):
        """Crear State para tests"""
        return State.objects.create(
            state_name="Valle del Cauca",
            state_code="VC",
            state_description="Departamento del Valle",
            state_country=self.test_country,
            state_is_active=True,
        )

    def get_valid_create_data(self):
        """Datos válidos para crear un estado"""
        return {
            "state_name": "Antioquia",
            "state_code": "ANT",
            "state_description": "Departamento de Antioquia",
            "state_is_active": True,
            "country_id": self.test_country.id,
        }

    def get_valid_update_data(self):
        """Datos válidos para actualizar un estado"""
        return {
            "state_name": "Valle Actualizado",
            "state_code": "VC",
            "state_description": "Descripción actualizada",
            "state_is_active": False,
            "country_id": self.test_country.id,
        }

    def get_invalid_create_data(self):
        """Datos inválidos para testear validaciones"""
        return {
            "state_name": "",
            "state_code": "TOOLONGCODE",
            "country_id": 99999,  # Country inexistente
        }

    def test_create_with_duplicate_code_fails(self):
        """Personalizado: No se puede crear con state_name y state_country duplicados"""
        self.client.force_authenticate(user=self.admin_user)

        data = self.get_valid_create_data()


        data["state_name"] = getattr(self.test_object, "state_name")
        data["state_country"] = (
            self.test_object.state_country.pk
        )  
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data) 
