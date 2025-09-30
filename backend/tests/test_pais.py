import pytest
from location.models import Pais
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_pais_creation():
    pais = Pais.objects.create(countryName="Brasil", countryCode="BR")
    assert pais.countryName == "Brasil"
    assert pais.countryCode == "BR"
    assert pais.countryState is True

@pytest.mark.django_db
def test_pais_str_returns_name():
    pais = Pais.objects.create(countryName="Argentina", countryCode="AR")
    assert str(pais) == "Argentina"

@pytest.mark.django_db
def test_pais_unique_country_name():
    pais = Pais.objects.create(countryName="Chile", countryCode="CL")
    with pytest.raises(Exception):
        Pais.objects.create(countryName="Chile", countryCode="CL2")

@pytest.mark.django_db
def test_pais_unique_country_code():
    pais = Pais.objects.create(countryName="Peru", countryCode="PE")
    with pytest.raises(Exception):
        Pais.objects.create(countryName="Peru2", countryCode="PE")


@pytest.mark.django_db
def test_country_name_max_length():
    # Crear un nombre más largo de 50 caracteres
    long_name = "A" * 51
    pais = Pais(countryName=long_name, countryCode="XX")
    with pytest.raises(ValidationError):
        pais.full_clean()  # valida restricciones de modelo antes de guardar

@pytest.mark.django_db
def test_country_code_max_length():
    long_code = "X" * 6
    pais = Pais(countryName="TestLand", countryCode=long_code)
    with pytest.raises(ValidationError):
        pais.full_clean()