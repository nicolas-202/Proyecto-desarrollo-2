import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from userInfo.models import Gender

# -------------------------------------------------------
# Pruebas del MODELO Gender
# -------------------------------------------------------

# Creación de un genero
@pytest.mark.django_db
def test_gender_creation():
    gender = Gender.objects.create(
        gender_name="Masculino",
        gender_code="M"
    )
    assert gender.gender_name == "Masculino"
    assert gender.gender_code == "M"
    assert gender.gender_is_active is True

# Método __str__
@pytest.mark.django_db
def test_gender_str_returns_name():
    gender = Gender.objects.create(
        gender_name="Femenino",
        gender_code="F"
    )
    assert str(gender) == "Femenino"

# Restricciones de unicidad
@pytest.mark.django_db
def test_gender_unique_constraints():
    Gender.objects.create(
        gender_name="Masculino",
        gender_code="M"
    )

    # Mismo nombre
    with pytest.raises(Exception):
        Gender.objects.create(
            gender_name="Masculino",
            gender_code="M2"
        )

    # Mismo código
    with pytest.raises(Exception):
        Gender.objects.create(
            gender_name="Masculino 2",
            gender_code="M2"
        )

# Validaciones de longitud y opcionalidad
@pytest.mark.django_db
def test_gender_name_max_length():
    long_name = "A" * 51
    gender = Gender(
        gender_name=long_name,
        gender_code="TEST"
    )
    with pytest.raises(ValidationError):
        gender.full_clean()

# Validaciones de longitud y opcionalidad
@pytest.mark.django_db
def test_gender_code_max_length():
    long_code = "ABCDE"
    gender = Gender(
        gender_name="aaaaaa",
        gender_code=long_code
    )
    with pytest.raises(ValidationError):
        gender.full_clean()

# Prueba de que description es opcional
@pytest.mark.django_db
def test_gender_description_optional():
    gender = Gender.objects.create(
        gender_name="a",
        gender_code="a"
    )
    assert gender.gender_description is None

# --------------------------------------------------------
# Pruebas de la API REST para Gender
# --------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def gender_created():
    return Gender.objects.create(
        gender_name="Masculino",
        gender_code="M"
    )

# Método POST para crear un genero
@pytest.mark.django_db
def test_api_create_gender(api_client):
    url = reverse("gender-list")  # Updated URL name
    data = {
        "gender_name": "Masculino",
        "gender_code": "M",
        "gender_description": "tin",
        "gender_is_active": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["gender_name"] == "Masculino"

# Método GET para listar generos
@pytest.mark.django_db
def test_api_list_gender(api_client, gender_created):
    url = reverse("gender-list")  # Updated URL name
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(c["gender_name"] == "Masculino" for c in response.data)

# Método GET para detalle de un genero
@pytest.mark.django_db
def test_api_get_gender_detail(api_client,  gender_created):
    url = reverse("gender-detail", args=[gender_created.id])  # Updated URL name
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["gender_name"] == "Masculino"

# Método PUT para actualizar un genero
@pytest.mark.django_db
def test_api_update_gender(api_client, gender_created):
    url = reverse("gender-detail", args=[gender_created.id])  # Updated URL name
    data = {
        "gender_name": "Masculino Updated",
        "gender_code": "M U",
        "gender_description": "Updated description",
        "gender_is_active": False,
    }
    response = api_client.put(url, data, format="json")
    assert response.status_code == 200
    gender_created.refresh_from_db()
    assert gender_created.gender_name == "Masculino Updated"
    assert gender_created.gender_is_active is False

# Método DELETE para eliminar un genero
@pytest.mark.django_db
def test_api_delete_gender(api_client,  gender_created):
    url = reverse("gender-detail", args=[gender_created.id])  # Updated URL name
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not Gender.objects.filter(id=gender_created.id).exists()