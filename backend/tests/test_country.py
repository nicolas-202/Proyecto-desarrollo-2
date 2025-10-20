# location/tests/test_country.py
from tests.base_test import BaseApiTest
from location.models import Country


class CountryViewSetTestCase(BaseApiTest):
    __test__ = True  # Indica a pytest que esta clase debe ser probada.
    """Tests para CountryViewSet"""
    
    # Configuración
    url_list_name = 'country-list'
    url_detail_name = 'country-detail'
    model_class = Country
    
    def create_test_object(self):
        """Crear Country para tests"""
        return Country.objects.create(
            country_name='Colombia',
            country_code='CO',
            country_description='País de prueba',
            country_is_active=True
        )
    
    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            'country_name': 'Argentina',
            'country_code': 'AR',
            'country_description': 'Nuevo país',
            'country_is_active': True
        }
    
    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            'country_name': 'Colombia Actualizada',
            'country_code': 'CO',
            'country_description': 'Nueva descripción',
            'country_is_active': False
        }
    
    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {
            'country_name': '',
            'country_code': 'TOOLONG',
            'country_is_active': True
        }