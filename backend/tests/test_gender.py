# userInfo/tests/test_gender.py
from tests.base_test import BaseApiTest
from userInfo.models import Gender


class GenderViewSetTestCase(BaseApiTest):
    """Tests para GenderViewSet"""

    __test__ = True  # Indica a pytest que esta clase DEBE ser probada

    # Configuración
    url_list_name = "gender-list"
    url_detail_name = "gender-detail"
    model_class = Gender

    def create_test_object(self):
        return Gender.objects.create(
            gender_name="Female Test",  # Cambia a un valor único
            gender_code="FT",  # Código único
            gender_description="Género de prueba",
            gender_is_active=True,
        )

    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            "gender_name": "Female",
            "gender_code": "F",
            "gender_description": "Nuevo género",
            "gender_is_active": True,
        }

    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            "gender_name": "Non-Binary",
            "gender_code": "NB",
            "gender_description": "Nueva descripción",
            "gender_is_active": False,
        }

    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {"gender_name": "", "gender_code": "TOOLONG", "gender_is_active": True}
