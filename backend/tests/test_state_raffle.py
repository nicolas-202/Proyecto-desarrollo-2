from tests.base_test import BaseApiTest
from raffleInfo.models import StateRaffle

class StateRaffleViewSetTestCase(BaseApiTest):
    """Tests para StateRaffleViewSet"""
    
    __test__ = True
    
    # Configuración
    url_list_name = 'state-raffle-list'
    url_detail_name = 'state-raffle-detail'
    model_class = StateRaffle
    
    def get_object_display_field(self):
        """Sobrescribe el nombre del campo principal"""
        return 'state_raffle_name'
    
    def get_code_field_name(self):
        """Sobrescribe el nombre del campo código"""
        return 'state_raffle_code'
    
    def get_description_field_name(self):
        """Sobrescribe el nombre del campo descripción"""
        return 'state_raffle_description'
    
    def get_is_active_field_name(self):
        """Sobrescribe el nombre del campo is_active"""
        return 'state_raffle_is_active'
    
    def get_unique_field_for_duplicate_test(self):
        """Sobrescribe el campo para prueba de duplicados"""
        return 'state_raffle_name'
    
    def create_test_object(self):
        return StateRaffle.objects.create(
            state_raffle_name='Test State',
            state_raffle_code='TST',
            state_raffle_description='Test state description',
            state_raffle_is_active=True
        )
    
    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            'state_raffle_name': 'New State',
            'state_raffle_code': 'NEW',
            'state_raffle_description': 'New state description',
            'state_raffle_is_active': True
        }
    
    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            'state_raffle_name': 'Updated State',
            'state_raffle_code': 'UPD',
            'state_raffle_description': 'Updated description',
            'state_raffle_is_active': False
        }
    
    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {
            'state_raffle_name': '',
            'state_raffle_code': 'TOOLONG',
            'state_raffle_is_active': True
        }