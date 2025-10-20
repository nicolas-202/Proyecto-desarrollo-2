# userInfo/tests/test_payment_method_type.py
from tests.base_test import BaseApiTest
from userInfo.models import PaymentMethodType


class PaymentMethodTypeViewSetTestCase(BaseApiTest):
    """Tests para PaymentMethodTypeViewSet"""
    
    __test__ = True  # Indica a pytest que esta clase DEBE ser probada
    
    # Configuración
    url_list_name = 'payment-method-type-list'
    url_detail_name = 'payment-method-type-detail'
    model_class = PaymentMethodType
    
    def create_test_object(self):
        """Crear PaymentMethodType para tests"""
        return PaymentMethodType.objects.create(
            payment_method_type_name='Credit Card',
            payment_method_type_code='CC',
            payment_method_type_description='Método de pago de prueba',
            payment_method_type_is_active=True
        )
    
    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            'payment_method_type_name': 'Debit Card',
            'payment_method_type_code': 'DC',
            'payment_method_type_description': 'Nuevo método de pago',
            'payment_method_type_is_active': True
        }
    
    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            'payment_method_type_name': 'PayPal',
            'payment_method_type_code': 'PP',
            'payment_method_type_description': 'Nueva descripción',
            'payment_method_type_is_active': False
        }
    
    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {
            'payment_method_type_name': '',
            'payment_method_type_code': 'TOOLONG',
            'payment_method_type_is_active': True
        }
    
    def get_object_display_field(self):
        """Usar el nombre correcto del campo"""
        return 'payment_method_type_name'
    
    def get_code_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'payment_method_type_code'
    
    def get_description_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'payment_method_type_description'
    
    def get_is_active_field_name(self):
        """Usar el nombre correcto del campo"""
        return 'payment_method_type_is_active'