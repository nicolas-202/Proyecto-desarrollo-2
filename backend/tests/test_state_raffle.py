# raflleInfo/tests/test_state_raffle.py
from tests.base_test import BaseApiTest
from raflleInfo.models import StateRaffle


class StateRaffleViewSetTestCase(BaseApiTest):
    """Tests para StateRaffleViewSet"""
    
    __test__ = True  # Indica a pytest que esta clase DEBE ser probada
    
    # Configuración
    url_list_name = 'state-raffle-list'
    url_detail_name = 'state-raffle-detail'
    model_class = StateRaffle
    
    def create_test_object(self):
        """Crear StateRaffle para tests"""
        return StateRaffle.objects.create(
            state_raffle_name='Active',
            state_raffle_code='ACT',
            state_raffle_description='Estado activo de prueba',
            state_raffle_is_active=True
        )
    
    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            'state_raffle_name': 'Pending',
            'state_raffle_code': 'PND',
            'state_raffle_description': 'Nuevo estado de rifa',
            'state_raffle_is_active': True
        }
    
    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            'state_raffle_name': 'Completed',
            'state_raffle_code': 'CMP',
            'state_raffle_description': 'Nueva descripción',
            'state_raffle_is_active': False
        }
    
    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {
            'state_raffle_name': '',
            'state_raffle_code': 'TOOLONG',
            'state_raffle_is_active': True
        }
    
    def get_object_display_field(self):
        """Usar el nombre correcto del campo"""
        return 'state_raffle_name'
    
    def get_code_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'state_raffle_code'
    
    def get_description_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'state_raffle_description'
    
    def get_is_active_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'state_raffle_is_active'
