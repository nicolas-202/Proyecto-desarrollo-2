import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from location.models import Country, State

# -------------------------------------------------------
# Pruebas del MODELO Country
# -------------------------------------------------------

#Creación de un país
@pytest.mark.django_db
def test_country_creation():
    country = Country.objects.create(country_name="Brazil", country_code="BR")
    assert country.country_name == "Brazil"
    assert country.country_code == "BR"
    assert country.country_is_active is True

# Método __str__
@pytest.mark.django_db
def test_country_str_returns_name():
    country = Country.objects.create(country_name="Argentina", country_code="AR")
    assert str(country) == "Argentina"


# Restricciones de unicidad
@pytest.mark.django_db
def test_country_unique_constraints():
    Country.objects.create(country_name="Chile", country_code="CL")

    # Mismo nombre
    with pytest.raises(Exception):
        Country.objects.create(country_name="Chile", country_code="CL2")

    # Mismo código
    with pytest.raises(Exception):
        Country.objects.create(country_name="Chile2", country_code="CL")


# Validaciones de longitud y opcionalidad
@pytest.mark.django_db
def test_country_name_max_length():
    long_name = "A" * 51
    country = Country(country_name=long_name, country_code="XX")
    with pytest.raises(ValidationError):
        country.full_clean()


# Validaciones de longitud y opcionalidad
@pytest.mark.django_db
def test_country_code_max_length():
    long_code = "ABCDE"
    country = Country(country_name="TestLand", country_code=long_code)
    with pytest.raises(ValidationError):
        country.full_clean()


# Prueba de que country_description es opcional
@pytest.mark.django_db
def test_country_description_optional():
    country = Country.objects.create(country_name="Ecuador", country_code="EC")
    assert country.country_description is None


# --------------------------------------------------------
# Pruebas de la API REST para Country
# --------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def country_created():
    return Country.objects.create(country_name="Brasil", country_code="BR")


# Método POST para crear un país
@pytest.mark.django_db
def test_api_create_country(api_client):
    url = reverse("country-list")
    data = {
        "country_name": "Colombia",
        "country_code": "CO",
        "country_description": "South American country",
        "country_is_active": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["country_name"] == "Colombia"


# Método GET para listar países
@pytest.mark.django_db
def test_api_list_countries(api_client, country_created):
    url = reverse("country-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(c["country_name"] == "Brasil" for c in response.data)


# Método GET para detalle de un país
@pytest.mark.django_db
def test_api_get_country_detail(api_client, country_created):
    url = reverse("country-detail", args=[country_created.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["country_name"] == "Brasil"


# Método PUT para actualizar un país
@pytest.mark.django_db
def test_api_update_country(api_client, country_created):
    url = reverse("country-detail", args=[country_created.id])
    data = {
        "country_name": "Brazil Updated",
        "country_code": "BR",
        "country_description": "Updated description",
        "country_is_active": False,
    }
    response = api_client.put(url, data, format="json")
    assert response.status_code == 200
    country_created.refresh_from_db()
    assert country_created.country_name == "Brazil Updated"
    assert country_created.country_is_active is False


# Método DELETE para eliminar un país
@pytest.mark.django_db
def test_api_delete_country(api_client, country_created):
    url = reverse("country-detail", args=[country_created.id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not Country.objects.filter(id=country_created.id).exists()
