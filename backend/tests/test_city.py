import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from location.models import Country, State, City

# -------------------------------------------------------
# FIXTURES
# -------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def country_created():
    return Country.objects.create(country_name="Colombia", country_code="CO")

@pytest.fixture
def state_created(country_created):
    return State.objects.create(
        state_name="Antioquia",
        state_code="ANT",
        state_description="Departamento del noroeste de Colombia",
        state_country=country_created,
        state_is_active=True,
    )

@pytest.fixture
def city_created(state_created):
    return City.objects.create(
        city_name="Medellín",
        city_code="MED",
        city_description="Capital de Antioquia",
        city_state=state_created,
        city_is_active=True,
    )
# -------------------------------------------------------
# PRUEBAS DEL MODELO STATE
# -------------------------------------------------------

# Creación de un estado
@pytest.mark.django_db
def test_city_creation(state_created):
    city = City.objects.create(
        city_name="La Ceja",
        city_code="LCJ",
        city_description="Municipio en Antioquia",
        city_state=state_created,
        city_is_active=True,
    )
    assert city.city_name == "La Ceja"
    assert city.city_state == state_created
    assert city.city_is_active is True


# Método __str__
@pytest.mark.django_db
def test_city_str_returns_name(state_created):
    city = City.objects.create(
        city_name="La Unión",
        city_code="LUN",
        city_state=state_created
    )
    assert str(city) == "La Unión"


# Restricciones de unicidad
@pytest.mark.django_db
def test_city_unique_constraints(state_created):
    City.objects.create(
        city_name="Necoclí",
        city_code="NEC",
        city_state=state_created
    )

    # Mismo nombre en el mismo país (debe fallar)
    with pytest.raises(Exception):
        City.objects.create(
            city_name="Necoclí",
            city_code="NEC2",
            city_state=state_created
        )

    # Mismo código de estado (debe fallar)
    with pytest.raises(Exception):
        City.objects.create(
            city_name="Necoclí2",
            city_code="NEC",
            city_state=state_created
        )


# Validación de longitud máxima del nombre
@pytest.mark.django_db
def test_city_name_max_length(state_created):
    long_name = "A" * 51
    city = City(
        city_name=long_name,
        city_code="XXX",
        city_state=state_created
    )
    with pytest.raises(ValidationError):
        city.full_clean()


# Validación de longitud máxima del código
@pytest.mark.django_db
def test_city_te_code_max_length(state_created):
    long_code = "ABCDE"
    city = City(
        city_name="Meta",
        city_code=long_code,
        city_state=state_created
    )
    with pytest.raises(ValidationError):
        city.full_clean()


# Validación de que la descripción es opcional
@pytest.mark.django_db
def test_city_description_optional(state_created):
    city = City.objects.create(
        city_name="Bello",
        city_code="BEL",
        city_state=state_created
    )
    assert city.city_description is None


# --------------------------------------------------------
# PRUEBAS DE LA API REST PARA STATE
# --------------------------------------------------------

# Método POST para crear un estado
@pytest.mark.django_db
def test_api_create_city(api_client, state_created):
    url = reverse("city-list")
    data = {
        "city_name": "Envigado",
        "city_code": "ENV",
        "city_description": "Ciudad de Antioquia",
        "city_state": state_created.id,
        "city_is_active": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["city_name"] == "Envigado"


# Método GET para listar estados
@pytest.mark.django_db
def test_api_list_cities(api_client, city_created):
    url = reverse("city-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(s["city_name"] == "Medellín" for s in response.data)


# Método GET para detalle de un estado
@pytest.mark.django_db
def test_api_get_city_detail(api_client, city_created):
    url = reverse("city-detail", args=[city_created.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["city_name"] == "Medellín"


# Método PUT para actualizar un estado
@pytest.mark.django_db
def test_api_update_city(api_client, city_created):
    url = reverse("city-detail", args=[city_created.id])
    data = {
        "city_name": "Medellín Actualizado",
        "city_code": "MED",
        "city_description": "Descripción actualizada",
        "city_state": city_created.city_state.id,
        "city_is_active": False,
    }
    response = api_client.put(url, data, format="json")
    assert response.status_code == 200
    city_created.refresh_from_db()
    assert city_created.city_name == "Medellín Actualizado"
    assert city_created.city_is_active is False


# Método DELETE para eliminar un estado
@pytest.mark.django_db
def test_api_delete_city(api_client, city_created):
    url = reverse("city-detail", args=[city_created.id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not City.objects.filter(id=city_created.id).exists()
