# raflleInfo/tests/test_prize_type.py
from tests.base_test import BaseApiTest
from raflleInfo.models import PrizeType


class PrizeTypeViewSetTestCase(BaseApiTest):
    """Tests para PrizeTypeViewSet"""
    
    __test__ = True  # Indica a pytest que esta clase DEBE ser probada
    
    # Configuración
    url_list_name = 'prize-type-list'
    url_detail_name = 'prize-type-detail'
    model_class = PrizeType
    
    def create_test_object(self):
        """Crear PrizeType para tests"""
        return PrizeType.objects.create(
            prize_type_name='Cash Prize',
            prize_type_code='CP',
            prize_type_description='Premio en efectivo de prueba',
            prize_type_is_active=True
        )
    
    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            'prize_type_name': 'Vehicle',
            'prize_type_code': 'VH',
            'prize_type_description': 'Nuevo tipo de premio',
            'prize_type_is_active': True
        }
    
    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            'prize_type_name': 'Electronics',
            'prize_type_code': 'EL',
            'prize_type_description': 'Nueva descripción',
            'prize_type_is_active': False
        }
    
    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {
            'prize_type_name': '',
            'prize_type_code': 'TOOLONG',
            'prize_type_is_active': True
        }
    
    def get_object_display_field(self):
        """Usar el nombre correcto del campo"""
        return 'prize_type_name'
    
    def get_code_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'prize_type_code'
    
    def get_description_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'prize_type_description'
    
    def get_is_active_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'prize_type_is_active'
