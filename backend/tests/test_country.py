# location/tests/test_country.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from location.models import Country, State, City
from user.models import User
from userInfo.models import Gender, DocumentType


class CountryViewSetTestCase(APITestCase):
    """
    Tests para CountryViewSet
    """
    
    @classmethod
    def setUpTestData(cls):
        """
        Crear datos UNA SOLA VEZ para todos los tests.
        Esto se ejecuta solo una vez al inicio, no antes de cada test.
        """
        # ========================================
        # 1. CREAR DEPENDENCIAS COMUNES
        # ========================================
        
        cls.gender = Gender.objects.create(
            gender_name="Male",
            gender_code="M"
        )
        
        cls.document_type = DocumentType.objects.create(
            document_type_name="Cedula de Ciudadania",
            document_type_code="CC"
        )
        
        # Crear Country, State, City para usuarios
        test_country_for_city = Country.objects.create(
            country_name="Test Country for City",
            country_code="TC"
        )
        
        test_state = State.objects.create(
            state_name="Test State",
            state_code="TS",
            state_country=test_country_for_city
        )
        
        cls.test_city = City.objects.create(
            city_name="Test City",
            city_code="TC",
            city_state=test_state
        )
        
        # ========================================
        # 2. CREAR USUARIOS (UNA SOLA VEZ)
        # ========================================
        
        cls.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            gender=cls.gender,
            document_type=cls.document_type,
            document_number='123456789',
            city=cls.test_city,
        )
        cls.admin_user.is_staff = True
        cls.admin_user.is_admin = True
        cls.admin_user.save()
        
        cls.regular_user = User.objects.create_user(
            email='user@test.com',
            password='user123',
            first_name='User',
            last_name='Test',
            gender=cls.gender,
            document_type=cls.document_type,
            document_number='0987654321',
            city=cls.test_city,
        )
        
        # ========================================
        # 3. URLs (no cambian)
        # ========================================
        
        cls.list_url = reverse('country-list')
    
    def setUp(self):
        """
        Se ejecuta ANTES de CADA test.
        Solo crear cosas que pueden ser modificadas/eliminadas en tests.
        """
        # Crear un Country fresco para cada test
        # (porque algunos tests lo modifican o eliminan)
        self.test_country = Country.objects.create(
            country_name='Colombia',
            country_code='CO',
            country_description='País de prueba',
            country_is_active=True
        )
        
        # URL de detalle (depende de test_country que es diferente cada vez)
        self.detail_url = reverse('country-detail', kwargs={'pk': self.test_country.pk})
    
    # ============================================
    # TESTS DE LIST
    # ============================================
    
    def test_list_countries_as_anonymous_user(self):
        """
        Usuario anónimo puede listar países
        """
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_countries_as_regular_user(self):
        """
        Usuario regular puede listar países
        """
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_countries_as_admin_user(self):
        """
        Admin puede listar países
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        # Verificar que Colombia está en los resultados
        country_names = [country['country_name'] for country in response.data]
        self.assertIn('Colombia', country_names)
    
    # ============================================
    # TESTS DE RETRIEVE
    # ============================================
    
    def test_retrieve_country_as_anonymous_user(self):
        """
        Usuario anónimo puede ver detalle de un país
        """
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country_name'], 'Colombia')
        self.assertEqual(response.data['country_code'], 'CO')
        self.assertIn('id', response.data)
    
    def test_retrieve_country_as_regular_user(self):
        """
        Usuario regular puede ver detalle
        """
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country_name'], 'Colombia')
    
    def test_retrieve_country_as_admin_user(self):
        """
        Admin puede ver detalle
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country_name'], 'Colombia')
    
    def test_retrieve_nonexistent_country_returns_404(self):
        """
        Intentar obtener país inexistente retorna 404
        """
        url = reverse('country-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ============================================
    # TESTS DE CREATE
    # ============================================
    
    def test_create_country_as_anonymous_user_fails(self):
        """
        Usuario anónimo NO puede crear países
        """
        data = {
            'country_name': 'Argentina',
            'country_code': 'AR',
            'country_description': 'Nuevo país',
            'country_is_active': True
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Country.objects.filter(country_name='Argentina').exists())
    
    def test_create_country_as_regular_user_fails(self):
        """
        Usuario regular NO puede crear países
        """
        self.client.force_authenticate(user=self.regular_user)
        
        data = {
            'country_name': 'Argentina',
            'country_code': 'AR',
            'country_description': 'Nuevo país',
            'country_is_active': True
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Country.objects.filter(country_name='Argentina').exists())
    
    def test_create_country_as_admin_user_success(self):
        """
        Admin puede crear países
        """
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'country_name': 'Argentina',
            'country_code': 'AR',
            'country_description': 'Nuevo país',
            'country_is_active': True
        }
        
        initial_count = Country.objects.count()
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Country.objects.count(), initial_count + 1)
        self.assertEqual(response.data['country_name'], 'Argentina')
        self.assertEqual(response.data['country_code'], 'AR')
        self.assertTrue(Country.objects.filter(country_name='Argentina').exists())
    
    def test_create_country_with_empty_name_fails(self):
        """
        No se puede crear país con nombre vacío
        """
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'country_name': '',
            'country_code': 'AR',
            'country_is_active': True
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country_name', response.data)
    
    def test_create_country_with_duplicate_name_fails(self):
        """
        No se puede crear país con nombre duplicado
        """
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'country_name': 'Colombia',  # Ya existe
            'country_code': 'CO2',
            'country_is_active': True
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country_name', response.data)
    
    def test_create_country_with_long_code_fails(self):
        """
        country_code debe tener máximo 4 caracteres
        """
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'country_name': 'Test Country',
            'country_code': 'VERYLONGCODE',
            'country_is_active': True
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country_code', response.data)
    
    def test_create_country_with_duplicate_code_fails(self):
        """
        No se puede crear país con código duplicado
        """
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'country_name': 'Colombia 2',
            'country_code': 'CO',  # Ya existe
            'country_is_active': True
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country_code', response.data)
    
    # ============================================
    # TESTS DE UPDATE
    # ============================================
    
    def test_update_country_as_anonymous_user_fails(self):
        """
        Usuario anónimo NO puede actualizar países
        """
        data = {
            'country_name': 'Colombia Actualizada',
            'country_code': 'CO',
            'country_description': 'Nueva descripción',
            'country_is_active': True
        }
        
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que NO se actualizó
        self.test_country.refresh_from_db()
        self.assertEqual(self.test_country.country_name, 'Colombia')
    
    def test_update_country_as_regular_user_fails(self):
        """
        Usuario regular NO puede actualizar países
        """
        self.client.force_authenticate(user=self.regular_user)
        
        data = {
            'country_name': 'Colombia Actualizada',
            'country_code': 'CO',
            'country_description': 'Nueva descripción',
            'country_is_active': True
        }
        
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verificar que NO se actualizó
        self.test_country.refresh_from_db()
        self.assertEqual(self.test_country.country_name, 'Colombia')
    
    def test_update_country_as_admin_user_success(self):
        """
        Admin puede actualizar países
        """
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'country_name': 'Colombia Actualizada',
            'country_code': 'CO',
            'country_description': 'Nueva descripción',
            'country_is_active': False
        }
        
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country_name'], 'Colombia Actualizada')
        self.assertEqual(response.data['country_description'], 'Nueva descripción')
        self.assertFalse(response.data['country_is_active'])
        
        # Verificar en BD
        self.test_country.refresh_from_db()
        self.assertEqual(self.test_country.country_name, 'Colombia Actualizada')
        self.assertEqual(self.test_country.country_description, 'Nueva descripción')
        self.assertFalse(self.test_country.country_is_active)
    
    # ============================================
    # TESTS DE PARTIAL UPDATE
    # ============================================
    
    def test_partial_update_country_as_anonymous_user_fails(self):
        """
        Usuario anónimo NO puede hacer partial update
        """
        data = {'country_description': 'Nueva descripción'}
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_partial_update_country_as_regular_user_fails(self):
        """
        Usuario regular NO puede hacer partial update
        """
        self.client.force_authenticate(user=self.regular_user)
        
        data = {'country_description': 'Nueva descripción'}
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_partial_update_country_as_admin_user_success(self):
        """
        Admin puede hacer partial update
        """
        self.client.force_authenticate(user=self.admin_user)
        
        # Solo actualizar descripción
        data = {'country_description': 'Descripción parcialmente actualizada'}
        
        original_name = self.test_country.country_name
        original_code = self.test_country.country_code
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country_description'], 'Descripción parcialmente actualizada')
        
        # Verificar que solo cambió la descripción
        self.test_country.refresh_from_db()
        self.assertEqual(self.test_country.country_description, 'Descripción parcialmente actualizada')
        self.assertEqual(self.test_country.country_name, original_name)
        self.assertEqual(self.test_country.country_code, original_code)
    
    def test_deactivate_country_as_admin(self):
        """
        Admin puede desactivar un país
        """
        self.client.force_authenticate(user=self.admin_user)
        
        self.assertTrue(self.test_country.country_is_active)
        
        response = self.client.patch(
            self.detail_url,
            {'country_is_active': False},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['country_is_active'])
        
        # Verificar en BD
        self.test_country.refresh_from_db()
        self.assertFalse(self.test_country.country_is_active)
    
    # ============================================
    # TESTS DE DELETE
    # ============================================
    
    def test_delete_country_as_anonymous_user_fails(self):
        """
        Usuario anónimo NO puede eliminar países
        """
        country_id = self.test_country.pk
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Country.objects.filter(pk=country_id).exists())
    
    def test_delete_country_as_regular_user_fails(self):
        """
        Usuario regular NO puede eliminar países
        """
        self.client.force_authenticate(user=self.regular_user)
        
        country_id = self.test_country.pk
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Country.objects.filter(pk=country_id).exists())
    
    def test_delete_country_as_admin_user_success(self):
        """
        Admin puede eliminar países
        """
        self.client.force_authenticate(user=self.admin_user)
        
        country_id = self.test_country.pk
        initial_count = Country.objects.count()
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Country.objects.count(), initial_count - 1)
        self.assertFalse(Country.objects.filter(pk=country_id).exists())