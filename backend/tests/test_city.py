# location/tests/test_city.py
from tests.base_test import BaseApiTest
from location.models import Country, State, City
from rest_framework import status

class CityViewSetTestCase(BaseApiTest):
    __test__ = True  # Indica a pytest que esta clase debe ser probada.
    """Tests para CityViewSet"""
    
    url_list_name = 'city-list'
    url_detail_name = 'city-detail'
    model_class = City
    
    @classmethod
    def setUpTestData(cls):
        """
        Crear dependencias extras (Country, State)
        """
        # Primero ejecutar el setUp de la clase base
        super().setUpTestData()
        
        # Crear Country
        cls.test_country_for_city = Country.objects.create(
            country_name='Colombia for Cities',
            country_code='COC',
            country_description='País para ciudades de prueba',
            country_is_active=True
        )
        
        # Crear States
        cls.test_state_for_city = State.objects.create(
            state_name='Valle del Cauca',
            state_code='VC',
            state_description='Departamento del Valle',
            state_country=cls.test_country_for_city,
            state_is_active=True
        )
        
        cls.other_state = State.objects.create(
            state_name='Antioquia',
            state_code='ANT',
            state_description='Departamento de Antioquia',
            state_country=cls.test_country_for_city,
            state_is_active=True
        )
    
    def create_test_object(self):
        """Crear City para tests"""
        return City.objects.create(
            city_name='Cali',
            city_code='CLI',
            city_description='Capital del Valle',
            city_state=self.test_state_for_city,
            city_is_active=True
        )
    
    def get_valid_create_data(self):
        """Datos válidos para crear una ciudad"""
        return {
            'city_name': 'Palmira',
            'city_code': 'PAL',
            'city_description': 'Ciudad del Valle',
            'city_is_active': True,
            'state_id': self.test_state_for_city.id
        }
    
    def get_valid_update_data(self):
        """Datos válidos para actualizar una ciudad"""
        return {
            'city_name': 'Cali Actualizada',
            'city_code': 'CLI',
            'city_description': 'Descripción actualizada',
            'city_is_active': False,
            'state_id': self.test_state_for_city.id
        }
    
    def get_invalid_create_data(self):
        """Datos inválidos para testear validaciones"""
        return {
            'city_name': '',
            'city_code': 'TOOLONGCODE',
            'state_id': 99999  # State inexistente
        }

    def test_create_with_duplicate_code_fails(self):
        """Personalizado: No se puede crear con city_name y city_state duplicados"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = self.get_valid_create_data()
        
        # Ajustar datos para duplicar la combinación única: city_name y city_state
        data['city_name'] = getattr(self.test_object, 'city_name')
        data['city_state'] = self.test_object.city_state.pk  # Usar el PK del estado existente
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)  # Error de unicidad combinada