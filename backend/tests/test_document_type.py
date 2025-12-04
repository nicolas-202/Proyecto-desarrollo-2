# userInfo/tests/test_document_type.py
from tests.base_test import BaseApiTest
from userInfo.models import DocumentType


class DocumentTypeViewSetTestCase(BaseApiTest):
    """Tests para DocumentTypeViewSet"""

    __test__ = True  # Indica a pytest que esta clase DEBE ser probada

    # Configuración
    url_list_name = "document-type-list"
    url_detail_name = "document-type-detail"
    model_class = DocumentType

    def create_test_object(self):
        return DocumentType.objects.create(
            document_type_name="Pasaporte Test",  # Cambia a un valor único
            document_type_code="PT",  # Código único
            document_type_description="Documento de prueba",
            document_type_is_active=True,
        )

    def get_valid_create_data(self):
        """Datos válidos para crear"""
        return {
            "document_type_name": "Tarjeta de Identidad",
            "document_type_code": "TI",
            "document_type_description": "Nuevo tipo de documento",
            "document_type_is_active": True,
        }

    def get_valid_update_data(self):
        """Datos válidos para actualizar"""
        return {
            "document_type_name": "Cedula Actualizada",
            "document_type_code": "CA",
            "document_type_description": "Nueva descripción",
            "document_type_is_active": False,
        }

    def get_invalid_create_data(self):
        """Datos inválidos"""
        return {
            "document_type_name": "",
            "document_type_code": "TOOLONG",
            "document_type_is_active": True,
        }

    def get_object_display_field(self):
        """Usar el nombre correcto del campo"""
        return "document_type_name"

    def get_code_field_name(self):
        """Usar el nombre correcto del campo"""
        return "document_type_code"

    def get_description_field_name(self):
        """Usar el nombre correcto del campo"""
        return "document_type_description"

    def get_is_active_field_name(self):
        """Usar el nombre correcto del campo"""
        return "document_type_is_active"
