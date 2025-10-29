from tests.base_test import BaseApiTest
from raffleInfo.models import PrizeType

class PrizeTypeViewSetTestCase(BaseApiTest):
    """Tests para PrizeTypeViewSet"""
    
    __test__ = True
    
    # Configuración
    url_list_name = 'prize-type-list'
    url_detail_name = 'prize-type-detail'
    model_class = PrizeType
    
    def get_object_display_field(self):
        """Sobrescribe el nombre del campo principal"""
        return 'prize_type_name'
    
    def get_code_field_name(self):
        """Sobrescribe el nombre del campo código"""
        return 'prize_type_code'
    
    def get_description_field_name(self):
        """Sobrescribe el nombre del campo descripción"""
        return 'prize_type_description'
    
    def get_is_active_field_name(self):
        """Sobrescribe el nombre del campo is_active"""
        return 'prize_type_is_active'
    
    def get_unique_field_for_duplicate_test(self):
        """Sobrescribe el campo para prueba de duplicados"""
        return 'prize_type_name'
    
    def create_test_object(self):
        return PrizeType.objects.create(
            prize_type_name='Test Prize',
            prize_type_code='TST',
            prize_type_description='Test prize description',
            prize_type_is_active=True
        )
    
    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            'prize_type_name': 'New Prize',
            'prize_type_code': 'NEW',
            'prize_type_description': 'New prize description',
            'prize_type_is_active': True
        }
    
    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            'prize_type_name': 'Updated Prize',
            'prize_type_code': 'UPD',
            'prize_type_description': 'Updated description',
            'prize_type_is_active': False
        }
    
    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {
            'prize_type_name': '',
            'prize_type_code': 'TOOLONG',
            'prize_type_is_active': True
        }