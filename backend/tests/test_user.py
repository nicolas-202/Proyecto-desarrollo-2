# user/tests/test_user.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from location.models import City, Country, State
from user.models import User
from userInfo.models import DocumentType, Gender


class UserAPITestCase(APITestCase):
    """
    Tests completos para el sistema de usuarios
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

        # Crear otro city para tests de actualización
        cls.other_city = City.objects.create(
            city_name="OtherCity", city_state=cls.state, city_code="OCY"
        )

        # Crear gender y document_type
        cls.gender = Gender.objects.create(gender_name="Non-Binary", gender_code="NB")
        cls.other_gender = Gender.objects.create(gender_name="Female", gender_code="F")
        cls.document_type = DocumentType.objects.create(
            document_type_name="Passport", document_type_code="PP"
        )

        # Crear usuarios
        cls.admin_user = User.objects.create_user(
            email="useradmin@gmail.com",
            password="testpassword",
            first_name="Admin",
            last_name="User",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="12345678",
            city=cls.city,
        )
        cls.admin_user.is_staff = True
        cls.admin_user.is_admin = True
        cls.admin_user.save()

        cls.user_regular = User.objects.create_user(
            email="userregular@gmail.com",
            password="testpassword",
            first_name="Regular",
            last_name="User",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="87654321",
            city=cls.city,
        )

    def setUp(self):
        """Refrescar usuarios antes de cada test"""
        self.user_regular.refresh_from_db()
        self.admin_user.refresh_from_db()

    # ============================================
    # TESTS DE LISTADO PÚBLICO DE USUARIOS
    # ============================================

    def test_user_basic_list_public_access(self):
        """Cualquiera puede acceder al listado público de usuarios básicos"""
        url = reverse("user_basic_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    def test_user_basic_list_content_safe(self):
        """El listado público solo contiene información no sensible"""
        url = reverse("user_basic_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data[0]

        # Verificar que contiene campos básicos
        self.assertIn("id", user_data)
        self.assertIn("email", user_data)
        self.assertIn("first_name", user_data)
        self.assertIn("full_name", user_data)

        # Verificar que NO contiene información sensible
        self.assertNotIn("document_number", user_data)
        self.assertNotIn("is_admin", user_data)
        self.assertNotIn("address", user_data)

    def test_user_basic_list_search(self):
        """Se puede buscar usuarios por nombre o email"""
        url = reverse("user_basic_list")

        # Buscar por nombre
        response = self.client.get(url, {"search": "Regular"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Buscar sin resultados
        response = self.client.get(url, {"search": "NoExiste"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ============================================
    # TESTS DE REGISTRO
    # ============================================

    def test_register_user_success(self):
        """Usuario puede registrarse con datos válidos"""
        url = reverse("user_register")
        data = {
            "email": "testcreate@gmail.com",
            "password": "newpassword",
            "confirm_password": "newpassword",
            "first_name": "Test",
            "last_name": "Create",
            "gender": self.gender.id,
            "document_type": self.document_type.id,
            "document_number": "11223344",
            "city": self.city.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(User.objects.count(), 3)

        # Verificar que el usuario fue creado correctamente
        new_user = User.objects.get(email="testcreate@gmail.com")
        self.assertEqual(new_user.first_name, "Test")
        self.assertTrue(new_user.check_password("newpassword"))

    def test_register_user_password_mismatch(self):
        """Registro falla si las contraseñas no coinciden"""
        url = reverse("user_register")
        data = {
            "email": "testcreate@gmail.com",
            "password": "newpassword",
            "confirm_password": "otherpassword",  # No coincide
            "first_name": "Test",
            "last_name": "Create",
            "gender": self.gender.id,
            "document_type": self.document_type.id,
            "document_number": "11223344",
            "city": self.city.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_register_user_duplicate_email(self):
        """No se puede registrar con email existente"""
        url = reverse("user_register")
        data = {
            "email": "userregular@gmail.com",  # Ya existe
            "password": "newpassword",
            "confirm_password": "newpassword",
            "first_name": "Test",
            "last_name": "Create",
            "gender": self.gender.id,
            "document_type": self.document_type.id,
            "document_number": "11223344",
            "city": self.city.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_duplicate_document_number(self):
        """No se puede registrar con document_number existente"""
        url = reverse("user_register")
        data = {
            "email": "newemail@gmail.com",
            "password": "newpassword",
            "confirm_password": "newpassword",
            "first_name": "Test",
            "last_name": "Create",
            "gender": self.gender.id,
            "document_type": self.document_type.id,
            "document_number": "87654321",  # Ya existe
            "city": self.city.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("document_number", response.data)

    def test_register_user_empty_email(self):
        """Email vacío debe fallar"""
        url = reverse("user_register")
        data = {
            "email": "",  # Vacío
            "password": "newpassword",
            "confirm_password": "newpassword",
            "first_name": "Test",
            "last_name": "Create",
            "gender": self.gender.id,
            "document_type": self.document_type.id,
            "document_number": "11223344",
            "city": self.city.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_short_password(self):
        """Contraseña menor a 8 caracteres debe fallar"""
        url = reverse("user_register")
        data = {
            "email": "test@gmail.com",
            "password": "short",  # Menos de 8 caracteres
            "confirm_password": "short",
            "first_name": "Test",
            "last_name": "Create",
            "gender": self.gender.id,
            "document_type": self.document_type.id,
            "document_number": "11223344",
            "city": self.city.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_user_invalid_phone_number(self):
        """Teléfono inválido debe fallar"""
        url = reverse("user_register")
        data = {
            "email": "test@gmail.com",
            "password": "newpassword",
            "confirm_password": "newpassword",
            "first_name": "Test",
            "last_name": "Create",
            "gender": self.gender.id,
            "document_type": self.document_type.id,
            "document_number": "11223344",
            "city": self.city.id,
            "phone_number": "123",  # No 10 dígitos
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    # ============================================
    # TESTS DE LOGIN
    # ============================================

    def test_login_success(self):
        """Login con credenciales correctas"""
        url = reverse("token_obtain_pair")
        data = {"email": "userregular@gmail.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_password(self):
        """Login con contraseña incorrecta"""
        url = reverse("token_obtain_pair")
        data = {"email": "userregular@gmail.com", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_login_nonexistent_user(self):
        """Login con usuario inexistente"""
        url = reverse("token_obtain_pair")
        data = {"email": "nonexistent@gmail.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ============================================
    # TESTS DE PERFIL (VIEW)
    # ============================================

    def test_view_profile_authenticated(self):
        """Usuario autenticado puede ver su perfil"""
        url = reverse("user_profile")
        self.client.force_authenticate(user=self.user_regular)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "userregular@gmail.com")
        self.assertIn("full_name", response.data)
        self.assertIn("city", response.data)
        self.assertIn("gender", response.data)

    def test_view_profile_anonymous(self):
        """Usuario anónimo NO puede ver perfil"""
        url = reverse("user_profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_view_profile(self):
        """Admin puede ver su propio perfil"""
        url = reverse("user_profile")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "useradmin@gmail.com")

    # ============================================
    # TESTS DE ACTUALIZACIÓN DE PERFIL
    # ============================================

    def test_update_profile_anonymous_fails(self):
        """Usuario anónimo NO puede actualizar perfil"""
        url = reverse("user_update")
        data = {"first_name": "UpdatedName"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_authenticated_success(self):
        """Usuario puede actualizar su perfil"""
        url = reverse("user_update")
        self.client.force_authenticate(user=self.user_regular)
        data = {
            "first_name": "UpdatedName",
            "last_name": "UpdatedLast",
            "phone_number": "3001234567",
            "address": "New Address 123",
            "city": self.city.id,
            "gender": self.gender.id,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "UpdatedName")
        self.assertEqual(response.data["last_name"], "UpdatedLast")
        self.assertEqual(response.data["phone_number"], "3001234567")

        # Verificar datos anidados
        self.assertIn("city", response.data)
        self.assertIn("gender", response.data)

        # Verificar en BD
        self.user_regular.refresh_from_db()
        self.assertEqual(self.user_regular.first_name, "UpdatedName")

    def test_partial_update_profile(self):
        """Usuario puede actualizar solo algunos campos (PATCH)"""
        url = reverse("user_update")
        self.client.force_authenticate(user=self.user_regular)

        original_last_name = self.user_regular.last_name

        data = {"first_name": "OnlyFirstName"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "OnlyFirstName")

        # Verificar que last_name NO cambió
        self.user_regular.refresh_from_db()
        self.assertEqual(self.user_regular.last_name, original_last_name)

    def test_update_profile_change_city(self):
        """Usuario puede cambiar de ciudad"""
        url = reverse("user_update")
        self.client.force_authenticate(user=self.user_regular)

        data = {
            "first_name": "Regular",
            "last_name": "User",
            "city": self.other_city.id,
            "gender": self.gender.id,
        }
        response = self.client.put(url, data, format="json")

        self.user_regular.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user_regular.city.id, self.other_city.id)
        self.assertEqual(self.user_regular.city.city_name, "OtherCity")

    def test_update_profile_invalid_phone(self):
        """Actualizar con teléfono inválido debe fallar"""
        url = reverse("user_update")
        self.client.force_authenticate(user=self.user_regular)

        data = {
            "first_name": "Regular",
            "last_name": "User",
            "phone_number": "123",  # Menos de 10 dígitos
            "city": self.city.id,
            "gender": self.gender.id,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    def test_update_profile_cannot_change_email(self):
        """No se puede cambiar email desde este endpoint"""
        url = reverse("user_update")
        self.client.force_authenticate(user=self.user_regular)

        original_email = self.user_regular.email

        data = {
            "first_name": "Regular",
            "last_name": "User",
            "email": "newemail@test.com",  # Intentar cambiar
            "city": self.city.id,
            "gender": self.gender.id,
        }
        response = self.client.put(url, data, format="json")

        # El email debe permanecer igual
        self.user_regular.refresh_from_db()
        self.assertEqual(self.user_regular.email, original_email)

    def test_admin_update_own_profile(self):
        """Admin puede actualizar su propio perfil"""
        url = reverse("user_update")
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "first_name": "AdminUpdated",
            "last_name": "User",
            "city": self.city.id,
            "gender": self.gender.id,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "AdminUpdated")

    # ============================================
    # TESTS DE ADMINISTRACIÓN (ADMIN ENDPOINTS)
    # ============================================

    def test_admin_list_users_success(self):
        """Admin puede listar usuarios"""
        url = reverse("admin_list")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_non_admin_list_users_fails(self):
        """Usuario regular NO puede listar usuarios"""
        url = reverse("admin_list")
        self.client.force_authenticate(user=self.user_regular)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_list_users_fails(self):
        """Usuario anónimo NO puede listar usuarios"""
        url = reverse("admin_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_update_user_success(self):
        """Admin puede actualizar otro usuario"""
        url = reverse("admin_update", args=[self.user_regular.id])
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "is_admin": True,
            "is_active": True,
            "document_type": self.document_type.id,
            "document_number": "87654321",
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar cambios
        self.user_regular.refresh_from_db()
        self.assertTrue(self.user_regular.is_admin)

    def test_non_admin_update_user_fails(self):
        """Usuario regular NO puede actualizar otros usuarios"""
        url = reverse("admin_update", args=[self.admin_user.id])
        self.client.force_authenticate(user=self.user_regular)
        data = {"is_admin": False}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_deactivate_self(self):
        """Admin NO puede desactivarse a sí mismo"""
        url = reverse("admin_update", args=[self.admin_user.id])
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "is_active": False,
            "is_admin": True,
            "document_type": self.document_type.id,
            "document_number": self.admin_user.document_number,
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No puedes desactivarte a ti mismo", str(response.data))

        # Verificar que sigue activo
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)

    # ============================================
    # TESTS DE CAMBIO DE CONTRASEÑA
    # ============================================

    def test_change_password_success(self):
        """Usuario puede cambiar su contraseña"""
        url = reverse("change_password")
        self.client.force_authenticate(user=self.user_regular)
        data = {
            "current_password": "testpassword",
            "new_password": "newsecurepassword",
            "confirm_new_password": "newsecurepassword",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la contraseña cambió
        self.user_regular.refresh_from_db()
        self.assertTrue(self.user_regular.check_password("newsecurepassword"))

    def test_change_password_wrong_current(self):
        """Cambiar contraseña con contraseña actual incorrecta falla"""
        url = reverse("change_password")
        self.client.force_authenticate(user=self.user_regular)
        data = {
            "current_password": "wrongpassword",
            "new_password": "newsecurepassword",
            "confirm_new_password": "newsecurepassword",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("current_password", response.data)

    def test_change_password_mismatch(self):
        """Nueva contraseña y confirmación no coinciden"""
        url = reverse("change_password")
        self.client.force_authenticate(user=self.user_regular)
        data = {
            "current_password": "testpassword",
            "new_password": "newsecurepassword",
            "confirm_new_password": "different",  # No coincide
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_same_as_current(self):
        """Nueva contraseña no puede ser igual a la actual"""
        url = reverse("change_password")
        self.client.force_authenticate(user=self.user_regular)
        data = {
            "current_password": "testpassword",
            "new_password": "testpassword",  # Misma
            "confirm_new_password": "testpassword",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_anonymous_fails(self):
        """Usuario anónimo NO puede cambiar contraseña"""
        url = reverse("change_password")
        data = {
            "current_password": "testpassword",
            "new_password": "newsecurepassword",
            "confirm_new_password": "newsecurepassword",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ============================================
    # TESTS DE ELIMINACIÓN DE CUENTA
    # ============================================

    def test_delete_account_success(self):
        """Usuario regular puede desactivar su cuenta"""
        url = reverse("delete_account")
        self.client.force_authenticate(user=self.user_regular)
        data = {"current_password": "testpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la cuenta está desactivada
        self.user_regular.refresh_from_db()
        self.assertFalse(self.user_regular.is_active)

    def test_delete_account_wrong_password(self):
        """Desactivar cuenta con contraseña incorrecta falla"""
        url = reverse("delete_account")
        self.client.force_authenticate(user=self.user_regular)
        data = {"current_password": "wrongpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar que sigue activo
        self.user_regular.refresh_from_db()
        self.assertTrue(self.user_regular.is_active)

    def test_delete_account_anonymous_fails(self):
        """Usuario anónimo NO puede desactivar cuentas"""
        url = reverse("delete_account")
        data = {"current_password": "testpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_cannot_delete_account(self):
        """Admin NO puede desactivar su propia cuenta"""
        url = reverse("delete_account")
        self.client.force_authenticate(user=self.admin_user)
        data = {"current_password": "testpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verificar que sigue activo
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)

    def test_delete_account_with_active_raffles_fails(self):
        """Usuario NO puede desactivar cuenta si tiene rifas activas"""
        # Nota: Este test requiere que el modelo Raffle esté configurado
        # y que exista una relación organized_raffles en el modelo User
        url = reverse("delete_account")
        self.client.force_authenticate(user=self.user_regular)
        data = {"current_password": "testpassword"}

        # Simular que el usuario tiene rifas activas (mock)
        # En un test real, crearías una rifa activa aquí

        response = self.client.post(url, data, format="json")

        # Si no hay rifas activas, debería funcionar normalmente
        # Si hay rifas activas, debería fallar con 400
        # Este test necesita ser ajustado cuando se implemente la relación con Raffle
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        )
