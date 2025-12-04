from datetime import date, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from location.models import City, Country, State
from user.models import User
from userInfo.models import DocumentType, Gender, PaymentMethod, PaymentMethodType


class PaymentMethodAPITestCase(APITestCase):
    """
    Tests para el sistema de métodos de pago
    """

    @classmethod
    def setUpTestData(cls):
        """Crear datos comunes para todos los tests"""
        # Crear location
        cls.country = Country.objects.create(
            country_name="TestCountry", country_code="TC"
        )
        cls.state = State.objects.create(
            state_name="TestState", state_country=cls.country, state_code="TS"
        )
        cls.city = City.objects.create(
            city_name="TestCity", city_state=cls.state, city_code="TCY"
        )

        # Crear gender y document_type
        cls.gender = Gender.objects.create(gender_name="Non-Binary", gender_code="NB")
        cls.document_type = DocumentType.objects.create(
            document_type_name="Passport", document_type_code="PP"
        )

        # Crear tipo de método de pago
        cls.payment_method_type = PaymentMethodType.objects.create(
            payment_method_type_name="Tarjeta de Crédito",
            payment_method_type_code="CC",
            payment_method_type_description="Tarjeta de crédito",
            payment_method_type_is_active=True,
        )

        # Crear usuarios
        cls.regular_user = User.objects.create_user(
            email="regular@test.com",
            password="testpass123",
            first_name="Regular",
            last_name="User",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="11111111",
            city=cls.city,
            is_admin=False,
        )

        cls.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="22222222",
            city=cls.city,
            is_admin=True,
        )

        cls.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
            first_name="Other",
            last_name="User",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="33333333",
            city=cls.city,
            is_admin=False,
        )

    def setUp(self):
        """Refrescar usuarios antes de cada test"""
        self.regular_user.refresh_from_db()
        self.admin_user.refresh_from_db()
        self.other_user.refresh_from_db()

        # URLs
        self.payment_method_list_url = reverse("payment-method-list")

    def create_payment_method(self, user=None, balance=1000.00):
        """Helper para crear método de pago con saldo"""
        if user is None:
            user = self.regular_user

        payment_method = PaymentMethod.objects.create(
            payment_method_type=self.payment_method_type,
            user=user,
            paymenth_method_holder_name="John Doe",
            paymenth_method_expiration_date=date.today() + timedelta(days=365),
            payment_method_balance=balance,  # Campo corregido
        )
        payment_method.set_card_number("1234567890123456")
        payment_method.save()
        return payment_method

    def get_valid_payment_method_data(self):
        """Datos válidos para crear método de pago"""
        return {
            "payment_method_type": self.payment_method_type.id,
            "paymenth_method_holder_name": "Jane Smith",
            "card_number": "9876543210987654",
            "paymenth_method_expiration_date": (
                date.today() + timedelta(days=365)
            ).isoformat(),
        }

    # Tests de permisos
    def test_anonymous_user_cannot_access(self):
        """Usuario anónimo no puede acceder"""
        response = self.client.get(self.payment_method_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_can_list_own_methods(self):
        """Usuario regular puede listar sus métodos"""
        self.client.force_authenticate(user=self.regular_user)
        self.create_payment_method(self.regular_user)

        response = self.client.get(self.payment_method_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_only_sees_own_methods(self):
        """Usuario solo ve sus propios métodos"""
        self.client.force_authenticate(user=self.regular_user)

        # Crear método para el usuario actual
        self.create_payment_method(self.regular_user)

        # Crear método para otro usuario
        self.create_payment_method(self.other_user)

        response = self.client.get(self.payment_method_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Solo ve el suyo

    # Tests de creación
    def test_create_payment_method_success(self):
        """Crear método de pago exitosamente"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentMethod.objects.count(), 1)

        # Verificar que el número no se muestra en la respuesta
        self.assertNotIn("card_number", response.data)
        self.assertIn("masked_card_number", response.data)
        self.assertEqual(response.data["masked_card_number"], "**** **** **** 7654")

    def test_create_with_invalid_card_number(self):
        """Fallar al crear con número inválido"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["card_number"] = "123"  # Muy corto

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_past_expiration_date(self):
        """Fallar al crear con fecha expirada"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["paymenth_method_expiration_date"] = (
            date.today() - timedelta(days=1)
        ).isoformat()

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests de validación de campos obligatorios
    def test_create_without_holder_name_fails(self):
        """Fallar al crear sin nombre del titular"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["paymenth_method_holder_name"] = ""  # Vacío

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn(
            "paymenth_method_holder_name", str(response.data["non_field_errors"])
        )

    def test_create_without_card_number_fails(self):
        """Fallar al crear sin número de tarjeta"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        del data["card_number"]  # Eliminar campo

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("card_number", str(response.data["non_field_errors"]))

    def test_create_with_empty_card_number_fails(self):
        """Fallar al crear con número de tarjeta vacío"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["card_number"] = ""  # Vacío

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("card_number", str(response.data["non_field_errors"]))

    def test_create_without_expiration_date_fails(self):
        """Fallar al crear sin fecha de expiración"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        del data["paymenth_method_expiration_date"]  # Eliminar campo

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn(
            "paymenth_method_expiration_date", str(response.data["non_field_errors"])
        )

    def test_create_with_whitespace_only_holder_name_fails(self):
        """Fallar al crear con nombre que solo tiene espacios"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["paymenth_method_holder_name"] = "   "  # Solo espacios

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("paymenth_method_holder_name", response.data)

    def test_create_with_very_long_holder_name_fails(self):
        """Fallar al crear con nombre muy largo"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["paymenth_method_holder_name"] = "A" * 101  # Muy largo

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("paymenth_method_holder_name", response.data)

    def test_holder_name_is_title_cased(self):
        """Verificar que el nombre se convierte a Title Case"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["paymenth_method_holder_name"] = "juan carlos pérez"

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["paymenth_method_holder_name"], "Juan Carlos Pérez"
        )

    def test_create_with_card_number_with_spaces_success(self):
        """Crear exitosamente con número que tiene espacios (se limpian automáticamente)"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["card_number"] = "1234 5678 9012 3456"  # Con espacios

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que se guardó correctamente
        payment_method = PaymentMethod.objects.get(id=response.data["id"])
        self.assertTrue(
            payment_method.check_card_number("1234567890123456")
        )  # Sin espacios

    def test_update_with_missing_required_fields_partial_success(self):
        """Actualización parcial sin campos obligatorios debe funcionar"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user)

        url = reverse("payment-method-detail", args=[payment_method.pk])
        # Solo actualizar un campo no obligatorio
        data = {"payment_method_is_active": False}

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["payment_method_is_active"])

    # Modificar test existente para asegurar que falla correctamente
    def test_create_with_invalid_holder_name(self):
        """Fallar al crear con nombre inválido"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_payment_method_data()
        data["paymenth_method_holder_name"] = "A"  # Muy corto

        response = self.client.post(self.payment_method_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("paymenth_method_holder_name", response.data)

    # Tests de actualización
    def test_update_own_payment_method(self):
        """Usuario puede actualizar su método"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user)

        url = reverse("payment-method-detail", args=[payment_method.pk])
        data = {"paymenth_method_holder_name": "Updated Name"}

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["paymenth_method_holder_name"], "Updated Name")

    def test_cannot_update_others_payment_method(self):
        """Usuario no puede actualizar método de otro"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.other_user)

        url = reverse("payment-method-detail", args=[payment_method.pk])
        data = {"paymenth_method_holder_name": "Hacker Name"}

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Test adicional para admin
    def test_admin_can_update_own_payment_method(self):
        """Admin puede actualizar su propio método de pago"""
        self.client.force_authenticate(user=self.admin_user)
        payment_method = self.create_payment_method(self.admin_user)

        url = reverse("payment-method-detail", args=[payment_method.pk])
        data = {
            "paymenth_method_holder_name": "Admin Updated Name",
            "card_number": "1111222233334444",
            "paymenth_method_expiration_date": (
                date.today() + timedelta(days=730)
            ).isoformat(),
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["paymenth_method_holder_name"], "Admin Updated Name"
        )

        # Verificar que el número se actualizó correctamente
        payment_method.refresh_from_db()
        self.assertTrue(payment_method.check_card_number("1111222233334444"))
        self.assertEqual(payment_method.last_digits, "4444")
        self.assertEqual(response.data["masked_card_number"], "**** **** **** 4444")

    # Tests de eliminación
    def test_delete_own_payment_method(self):
        """Usuario puede eliminar su método"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user)

        url = reverse("payment-method-detail", args=[payment_method.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PaymentMethod.objects.count(), 0)

    def test_cannot_delete_others_payment_method(self):
        """Usuario no puede eliminar método de otro"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.other_user)

        url = reverse("payment-method-detail", args=[payment_method.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Tests de acciones personalizadas
    def test_deactivate_payment_method(self):
        """Desactivar método de pago"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user)

        url = reverse("payment-method-deactivate", args=[payment_method.pk])
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment_method.refresh_from_db()
        self.assertFalse(payment_method.payment_method_is_active)

    def test_verify_card_number_success(self):
        """Verificar número de tarjeta correctamente"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user)

        url = reverse("payment-method-verify-card", args=[payment_method.pk])
        data = {"card_number": "1234567890123456"}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_valid"])

    def test_verify_card_number_fail(self):
        """Fallar verificación con número incorrecto"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user)

        url = reverse("payment-method-verify-card", args=[payment_method.pk])
        data = {"card_number": "9999999999999999"}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_valid"])

    def test_verify_card_without_number(self):
        """Fallar verificación sin número"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user)

        url = reverse("payment-method-verify-card", args=[payment_method.pk])
        data = {}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_balance_not_exposed_in_api(self):
        """Verificar que el saldo no se expone en la API"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user, balance=500.00)

        url = reverse("payment-method-detail", args=[payment_method.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que el saldo NO está en la respuesta
        self.assertNotIn("payment_method_balance", response.data)

    def test_check_sufficient_balance(self):
        """Verificar saldo suficiente"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user, balance=500.00)

        url = reverse("payment-method-check-balance", args=[payment_method.pk])
        data = {"amount": "100.00"}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["has_sufficient_balance"])

    def test_check_insufficient_balance(self):
        """Verificar saldo insuficiente"""
        self.client.force_authenticate(user=self.regular_user)
        payment_method = self.create_payment_method(self.regular_user, balance=50.00)

        url = reverse("payment-method-check-balance", args=[payment_method.pk])
        data = {"amount": "100.00"}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["has_sufficient_balance"])

    def test_balance_manipulation_methods(self):
        """Probar métodos de manipulación de saldo"""
        payment_method = self.create_payment_method(balance=100.00)

        # Verificar saldo inicial
        self.assertEqual(payment_method.payment_method_balance, 100.00)

        # Deducir saldo
        result = payment_method.deduct_balance(50.00)
        self.assertTrue(result)
        self.assertEqual(payment_method.payment_method_balance, 50.00)

        # Intentar deducir más del saldo disponible
        result = payment_method.deduct_balance(100.00)
        self.assertFalse(result)
        self.assertEqual(payment_method.payment_method_balance, 50.00)  # No cambió

        # Agregar saldo
        payment_method.add_balance(75.00)
        self.assertEqual(payment_method.payment_method_balance, 125.00)
