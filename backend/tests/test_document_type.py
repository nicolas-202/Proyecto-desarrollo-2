import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from userInfo.models import DocumentType

# -------------------------------------------------------
# Pruebas del MODELO DocumentType
# -------------------------------------------------------

# Creación de un tipo de documento
@pytest.mark.django_db
def test_document_type_creation():
    document_type = DocumentType.objects.create(
        document_type_name="Passport",
        document_type_code="PASS"
    )
    assert document_type.document_type_name == "Passport"
    assert document_type.document_type_code == "PASS"
    assert document_type.document_type_is_active is True

# Método __str__
@pytest.mark.django_db
def test_document_type_str_returns_name():
    document_type = DocumentType.objects.create(
        document_type_name="ID Card",
        document_type_code="IDC"
    )
    assert str(document_type) == "ID Card"

# Restricciones de unicidad
@pytest.mark.django_db
def test_document_type_unique_constraints():
    DocumentType.objects.create(
        document_type_name="Driver License",
        document_type_code="DL"
    )

    # Mismo nombre
    with pytest.raises(Exception):
        DocumentType.objects.create(
            document_type_name="Driver License",
            document_type_code="DL2"
        )

    # Mismo código
    with pytest.raises(Exception):
        DocumentType.objects.create(
            document_type_name="Driver License 2",
            document_type_code="DL"
        )

# Validaciones de longitud y opcionalidad
@pytest.mark.django_db
def test_document_type_name_max_length():
    long_name = "A" * 51
    document_type = DocumentType(
        document_type_name=long_name,
        document_type_code="TEST"
    )
    with pytest.raises(ValidationError):
        document_type.full_clean()

# Validaciones de longitud y opcionalidad
@pytest.mark.django_db
def test_document_type_code_max_length():
    long_code = "ABCDE"
    document_type = DocumentType(
        document_type_name="Test Document",
        document_type_code=long_code
    )
    with pytest.raises(ValidationError):
        document_type.full_clean()

# Prueba de que document_type_description es opcional
@pytest.mark.django_db
def test_document_type_description_optional():
    document_type = DocumentType.objects.create(
        document_type_name="Visa",
        document_type_code="VISA"
    )
    assert document_type.document_type_description is None

# --------------------------------------------------------
# Pruebas de la API REST para DocumentType
# --------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def document_type_created():
    return DocumentType.objects.create(
        document_type_name="Passport",
        document_type_code="PASS"
    )

# Método POST para crear un tipo de documento
@pytest.mark.django_db
def test_api_create_document_type(api_client):
    url = reverse("documentType-list")  # Updated URL name
    data = {
        "document_type_name": "National ID",
        "document_type_code": "NID",
        "document_type_description": "National identification document",
        "document_type_is_active": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["document_type_name"] == "National ID"

# Método GET para listar tipos de documento
@pytest.mark.django_db
def test_api_list_document_types(api_client, document_type_created):
    url = reverse("documentType-list")  # Updated URL name
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(c["document_type_name"] == "Passport" for c in response.data)

# Método GET para detalle de un tipo de documento
@pytest.mark.django_db
def test_api_get_document_type_detail(api_client, document_type_created):
    url = reverse("documentType-detail", args=[document_type_created.id])  # Updated URL name
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["document_type_name"] == "Passport"

# Método PUT para actualizar un tipo de documento
@pytest.mark.django_db
def test_api_update_document_type(api_client, document_type_created):
    url = reverse("documentType-detail", args=[document_type_created.id])  # Updated URL name
    data = {
        "document_type_name": "Passport Updated",
        "document_type_code": "PASS",
        "document_type_description": "Updated description",
        "document_type_is_active": False,
    }
    response = api_client.put(url, data, format="json")
    assert response.status_code == 200
    document_type_created.refresh_from_db()
    assert document_type_created.document_type_name == "Passport Updated"
    assert document_type_created.document_type_is_active is False

# Método DELETE para eliminar un tipo de documento
@pytest.mark.django_db
def test_api_delete_document_type(api_client, document_type_created):
    url = reverse("documentType-detail", args=[document_type_created.id])  # Updated URL name
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not DocumentType.objects.filter(id=document_type_created.id).exists()