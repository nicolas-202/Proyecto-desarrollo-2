import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from userInfo.models import PaymentMethodType # Assuming PaymentMethodType is in userInfo.models

# -------------------------------------------------------
# Pruebas del MODELO PaymentMethodType
# -------------------------------------------------------

# Creación de un tipo de método de pago
@pytest.mark.django_db
def test_payment_method_type_creation():
    pmt = PaymentMethodType.objects.create(
        payment_method_type_name="Tarjeta de Crédito",
        payment_method_type_code="CC"
    )
    assert pmt.payment_method_type_name == "Tarjeta de Crédito"
    assert pmt.payment_method_type_code == "CC"
    assert pmt.payment_method_type_is_active is True

# Método __str__
@pytest.mark.django_db
def test_payment_method_type_str_returns_name():
    pmt = PaymentMethodType.objects.create(
        payment_method_type_name="Transferencia Bancaria",
        payment_method_type_code="TB"
    )
    assert str(pmt) == "Transferencia Bancaria"

# Restricciones de unicidad
@pytest.mark.django_db
def test_payment_method_type_unique_constraints():
    PaymentMethodType.objects.create(
        payment_method_type_name="Efectivo",
        payment_method_type_code="EF"
    )

    # Mismo nombre
    with pytest.raises(Exception):
        PaymentMethodType.objects.create(
            payment_method_type_name="Efectivo",
            payment_method_type_code="EF2"
        )

    # Mismo código
    with pytest.raises(Exception):
        PaymentMethodType.objects.create(
            payment_method_type_name="Efectivo 2",
            payment_method_type_code="EF"
        )

# Validaciones de longitud y opcionalidad: Nombre (max_length=50)
@pytest.mark.django_db
def test_payment_method_type_name_max_length():
    long_name = "A" * 51
    pmt = PaymentMethodType(
        payment_method_type_name=long_name,
        payment_method_type_code="TEST"
    )
    with pytest.raises(ValidationError):
        pmt.full_clean()

# Validaciones de longitud y opcionalidad: Código (max_length=4)
@pytest.mark.django_db
def test_payment_method_type_code_max_length():
    long_code = "ABCDE"
    pmt = PaymentMethodType(
        payment_method_type_name="Prueba",
        payment_method_type_code=long_code
    )
    with pytest.raises(ValidationError):
        pmt.full_clean()

# Prueba de que description es opcional
@pytest.mark.django_db
def test_payment_method_type_description_optional():
    pmt = PaymentMethodType.objects.create(
        payment_method_type_name="a",
        payment_method_type_code="a"
    )
    assert pmt.payment_method_type_description is None

# --------------------------------------------------------
# Pruebas de la API REST para PaymentMethodType
# --------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def pmt_created():
    return PaymentMethodType.objects.create(
        payment_method_type_name="Tarjeta de Débito",
        payment_method_type_code="TD"
    )

# Método POST para crear un tipo de método de pago
@pytest.mark.django_db
def test_api_create_payment_method_type(api_client):
    url = reverse("paymentMethodType-list") # Assuming the URL name is 'paymentmethodtype-list'
    data = {
        "payment_method_type_name": "Cheque",
        "payment_method_type_code": "CH",
        "payment_method_type_description": "Pago con cheque",
        "payment_method_type_is_active": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["payment_method_type_name"] == "Cheque"

# Método GET para listar tipos de métodos de pago
@pytest.mark.django_db
def test_api_list_payment_method_type(api_client, pmt_created):
    url = reverse("paymentMethodType-list") # Assuming the URL name is 'paymentmethodtype-list'
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(c["payment_method_type_name"] == "Tarjeta de Débito" for c in response.data)

# Método GET para detalle de un tipo de método de pago
@pytest.mark.django_db
def test_api_get_payment_method_type_detail(api_client, pmt_created):
    url = reverse("paymentMethodType-detail", args=[pmt_created.id]) # Assuming the URL name is 'paymentmethodtype-detail'
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["payment_method_type_name"] == "Tarjeta de Débito"

# Método PUT para actualizar un tipo de método de pago
@pytest.mark.django_db
def test_api_update_payment_method_type(api_client, pmt_created):
    url = reverse("paymentMethodType-detail", args=[pmt_created.id]) # Assuming the URL name is 'paymentmethodtype-detail'
    data = {
        "payment_method_type_name": "Tarjeta de Débito Updated",
        "payment_method_type_code": "TD U",
        "payment_method_type_description": "Updated description",
        "payment_method_type_is_active": False,
    }
    response = api_client.put(url, data, format="json")
    assert response.status_code == 200
    pmt_created.refresh_from_db()
    assert pmt_created.payment_method_type_name == "Tarjeta de Débito Updated"
    assert pmt_created.payment_method_type_is_active is False

# Método DELETE para eliminar un tipo de método de pago
@pytest.mark.django_db
def test_api_delete_payment_method_type(api_client, pmt_created):
    url = reverse("paymentMethodType-detail", args=[pmt_created.id]) # Assuming the URL name is 'paymentmethodtype-detail'
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not PaymentMethodType.objects.filter(id=pmt_created.id).exists()