import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from location.models import Country, State

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
        state_state=True,
    )

# -------------------------------------------------------
# PRUEBAS DEL MODELO STATE
# -------------------------------------------------------

# Creación de un estado
@pytest.mark.django_db
def test_state_creation(country_created):
    state = State.objects.create(
        state_name="Cundinamarca",
        state_code="CUN",
        state_description="Departamento central",
        state_country=country_created,
        state_state=True,
    )
    assert state.state_name == "Cundinamarca"
    assert state.state_country == country_created
    assert state.state_state is True


# Método __str__
@pytest.mark.django_db
def test_state_str_returns_name(country_created):
    state = State.objects.create(
        state_name="Valle del Cauca",
        state_code="VAL",
        state_country=country_created
    )
    assert str(state) == "Valle del Cauca"


# Restricciones de unicidad
@pytest.mark.django_db
def test_state_unique_constraints(country_created):
    State.objects.create(
        state_name="Santander",
        state_code="SAN",
        state_country=country_created
    )

    # Mismo nombre en el mismo país (debe fallar)
    with pytest.raises(Exception):
        State.objects.create(
            state_name="Santander",
            state_code="SAN2",
            state_country=country_created
        )

    # Mismo código de estado (debe fallar)
    with pytest.raises(Exception):
        State.objects.create(
            state_name="Santander Norte",
            state_code="SAN",
            state_country=country_created
        )


# Validación de longitud máxima del nombre
@pytest.mark.django_db
def test_state_name_max_length(country_created):
    long_name = "A" * 51
    state = State(
        state_name=long_name,
        state_code="XXX",
        state_country=country_created
    )
    with pytest.raises(ValidationError):
        state.full_clean()


# Validación de longitud máxima del código
@pytest.mark.django_db
def test_state_code_max_length(country_created):
    long_code = "ABCDE"
    state = State(
        state_name="Meta",
        state_code=long_code,
        state_country=country_created
    )
    with pytest.raises(ValidationError):
        state.full_clean()


# Validación de que la descripción es opcional
@pytest.mark.django_db
def test_state_description_optional(country_created):
    state = State.objects.create(
        state_name="Bolívar",
        state_code="BOL",
        state_country=country_created
    )
    assert state.state_description is None


# --------------------------------------------------------
# PRUEBAS DE LA API REST PARA STATE
# --------------------------------------------------------

# Método POST para crear un estado
@pytest.mark.django_db
def test_api_create_state(api_client, country_created):
    url = reverse("state-list")
    data = {
        "state_name": "Quindío",
        "state_code": "QUI",
        "state_description": "Departamento cafetero",
        "state_country": country_created.id,
        "state_state": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["state_name"] == "Quindío"


# Método GET para listar estados
@pytest.mark.django_db
def test_api_list_states(api_client, state_created):
    url = reverse("state-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(s["state_name"] == "Antioquia" for s in response.data)


# Método GET para detalle de un estado
@pytest.mark.django_db
def test_api_get_state_detail(api_client, state_created):
    url = reverse("state-detail", args=[state_created.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["state_name"] == "Antioquia"


# Método PUT para actualizar un estado
@pytest.mark.django_db
def test_api_update_state(api_client, state_created):
    url = reverse("state-detail", args=[state_created.id])
    data = {
        "state_name": "Antioquia Actualizado",
        "state_code": "ANT",
        "state_description": "Descripción actualizada",
        "state_country": state_created.state_country.id,
        "state_state": False,
    }
    response = api_client.put(url, data, format="json")
    assert response.status_code == 200
    state_created.refresh_from_db()
    assert state_created.state_name == "Antioquia Actualizado"
    assert state_created.state_state is False


# Método DELETE para eliminar un estado
@pytest.mark.django_db
def test_api_delete_state(api_client, state_created):
    url = reverse("state-detail", args=[state_created.id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not State.objects.filter(id=state_created.id).exists()
