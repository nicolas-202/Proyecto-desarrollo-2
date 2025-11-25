# tests/base_viewset_test.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from location.models import Country, State, City
from user.models import User
from userInfo.models import Gender, DocumentType


class BaseApiTest(APITestCase,):
    __test__ = False  
    """
    Clase base para testear ViewSets con permisos IsAdminOrReadOnly.
    
    Las clases hijas deben definir:
    - url_list_name: 'country-list', 'state-list', etc.
    - url_detail_name: 'country-detail', 'state-detail', etc.
    - model_class: Country, State, City, etc.
    - get_valid_create_data(): retorna diccionario con datos válidos para crear
    - get_valid_update_data(): retorna diccionario con datos válidos para actualizar
    - get_invalid_create_data(): retorna diccionario con datos inválidos
    - create_test_object(): crea y retorna una instancia del modelo para tests
    - get_object_display_field(): nombre del campo principal (ej: 'country_name')
    """
    
    # Variables que DEBEN ser definidas en clases hijas
    url_list_name = None
    url_detail_name = None
    model_class = None
    
    @classmethod
    def setUpTestData(cls):
        """
        Crear datos comunes UNA SOLA VEZ para todos los tests.
        """
        # Crear dependencias para usuarios
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
        
        # Crear usuarios
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
        
        # URL de lista
        cls.list_url = reverse(cls.url_list_name)
    
    def setUp(self):
        """
        Crear objeto de prueba antes de cada test.
        """
        self.test_object = self.create_test_object()
        self.detail_url = reverse(self.url_detail_name, kwargs={'pk': self.test_object.pk})
    
    # ============================================
    # MÉTODOS QUE DEBEN SER IMPLEMENTADOS
    # ============================================
    
    def create_test_object(self):
        """
        Crear y retornar objeto del modelo para tests.
        DEBE ser implementado en clases hijas.
        """
        raise NotImplementedError("Debes implementar create_test_object()")
    
    def get_valid_create_data(self):
        """
        Retornar datos válidos para crear objeto.
        DEBE ser implementado en clases hijas.
        """
        raise NotImplementedError("Debes implementar get_valid_create_data()")
    
    def get_valid_update_data(self):
        """
        Retornar datos válidos para actualizar objeto.
        DEBE ser implementado en clases hijas.
        """
        raise NotImplementedError("Debes implementar get_valid_update_data()")
    
    def get_invalid_create_data(self):
        """
        Retornar datos inválidos para testear validaciones.
        DEBE ser implementado en clases hijas.
        """
        raise NotImplementedError("Debes implementar get_invalid_create_data()")
    
    def get_object_display_field(self):
        """
        Retornar nombre del campo principal del objeto.
        Por defecto: '{model}_name'
        Puede ser sobrescrito en clases hijas.
        """
        return f"{self.model_class.__name__.lower()}_name"
    
    def get_unique_field_for_duplicate_test(self):
        """
        Retornar nombre del campo único para test de duplicados.
        Por defecto: '{model}_name'
        Puede ser sobrescrito en clases hijas.
        """
        return self.get_object_display_field()
    
    def get_code_field_name(self):
        """
        Retornar nombre del campo de código.
        Por defecto: '{model}_code'
        Puede ser sobrescrito en clases hijas.
        """
        return f"{self.model_class.__name__.lower()}_code"
    
    def get_description_field_name(self):
        """
        Retornar nombre del campo de descripción.
        Por defecto: '{model}_description'
        Puede ser sobrescrito en clases hijas.
        """
        return f"{self.model_class.__name__.lower()}_description"
    
    def get_is_active_field_name(self):
        """
        Retornar nombre del campo de is_active.
        Por defecto: '{model}_is_active'
        Puede ser sobrescrito en clases hijas.
        """
        return f"{self.model_class.__name__.lower()}_is_active"
    # ============================================
    # TESTS DE LIST
    # ============================================
    
    def test_list_as_anonymous_user(self):
        """Usuario anónimo puede listar"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_as_regular_user(self):
        """Usuario regular puede listar"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_as_admin_user(self):
        """Admin puede listar"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
    
    # ============================================
    # TESTS DE RETRIEVE
    # ============================================
    
    def test_retrieve_as_anonymous_user(self):
        """Usuario anónimo puede ver detalle"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        display_field = self.get_object_display_field()
        expected_value = getattr(self.test_object, display_field)
        self.assertEqual(response.data[display_field], expected_value)
    
    def test_retrieve_as_regular_user(self):
        """Usuario regular puede ver detalle"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        display_field = self.get_object_display_field()
        expected_value = getattr(self.test_object, display_field)
        self.assertEqual(response.data[display_field], expected_value)
    
    def test_retrieve_as_admin_user(self):
        """Admin puede ver detalle"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        display_field = self.get_object_display_field()
        expected_value = getattr(self.test_object, display_field)
        self.assertEqual(response.data[display_field], expected_value)
    
    def test_retrieve_nonexistent_returns_404(self):
        """Intentar obtener objeto inexistente retorna 404"""
        url = reverse(self.url_detail_name, kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ============================================
    # TESTS DE CREATE
    # ============================================
    
    def test_create_as_anonymous_user_fails(self):
        """Usuario anónimo NO puede crear"""
        data = self.get_valid_create_data()
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_as_regular_user_fails(self):
        """Usuario regular NO puede crear"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_create_data()
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_as_admin_user_success(self):
        """Admin puede crear"""
        self.client.force_authenticate(user=self.admin_user)
        data = self.get_valid_create_data()
        
        initial_count = self.model_class.objects.count()
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model_class.objects.count(), initial_count + 1)
        self.assertIn('id', response.data)
    
    def test_create_with_empty_name_fails(self):
        """No se puede crear con nombre vacío"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = self.get_valid_create_data()
        display_field = self.get_object_display_field()
        data[display_field] = ''
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(display_field, response.data)
    
    def test_create_with_duplicate_name_fails(self):
        """No se puede crear con nombre duplicado"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = self.get_valid_create_data()
        unique_field = self.get_unique_field_for_duplicate_test()
        data[unique_field] = getattr(self.test_object, unique_field)
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_with_long_code_fails(self):
        """Código no puede ser muy largo"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = self.get_valid_create_data()
        code_field = self.get_code_field_name()
        data[code_field] = 'VERYLONGCODE'
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(code_field, response.data)
    
    def test_create_with_duplicate_code_fails(self):
        """No se puede crear con código duplicado"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = self.get_valid_create_data()
        code_field = self.get_code_field_name()
        data[code_field] = getattr(self.test_object, code_field)
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(code_field, response.data)
    
    # ============================================
    # TESTS DE UPDATE
    # ============================================
    
    def test_update_as_anonymous_user_fails(self):
        """Usuario anónimo NO puede actualizar"""
        data = self.get_valid_update_data()
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_as_regular_user_fails(self):
        """Usuario regular NO puede actualizar"""
        self.client.force_authenticate(user=self.regular_user)
        data = self.get_valid_update_data()
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_as_admin_user_success(self):
        """Admin puede actualizar"""
        self.client.force_authenticate(user=self.admin_user)
        data = self.get_valid_update_data()
        
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # ============================================
    # TESTS DE PARTIAL UPDATE
    # ============================================
    
    def test_partial_update_as_anonymous_user_fails(self):
        """Usuario anónimo NO puede hacer partial update"""
        description_field = self.get_description_field_name()
        data = {description_field: 'Nueva descripción'}
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_partial_update_as_regular_user_fails(self):
        """Usuario regular NO puede hacer partial update"""
        self.client.force_authenticate(user=self.regular_user)
        
        description_field = self.get_description_field_name()
        data = {description_field: 'Nueva descripción'}
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_partial_update_as_admin_user_success(self):
        """Admin puede hacer partial update"""
        self.client.force_authenticate(user=self.admin_user)
        
        description_field = self.get_description_field_name()
        data = {description_field: 'Descripción actualizada'}
        
        display_field = self.get_object_display_field()
        code_field = self.get_code_field_name()
        
        original_name = getattr(self.test_object, display_field)
        original_code = getattr(self.test_object, code_field)
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que solo cambió la descripción
        self.test_object.refresh_from_db()
        self.assertEqual(getattr(self.test_object, display_field), original_name)
        self.assertEqual(getattr(self.test_object, code_field), original_code)
    
    def test_deactivate_as_admin(self):
        """Admin puede desactivar"""
        self.client.force_authenticate(user=self.admin_user)
        
        is_active_field = self.get_is_active_field_name()
        
        response = self.client.patch(
            self.detail_url,
            {is_active_field: False},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data[is_active_field])
        
        # Verificar en BD
        self.test_object.refresh_from_db()
        self.assertFalse(getattr(self.test_object, is_active_field))
    
    # ============================================
    # TESTS DE DELETE
    # ============================================
    
    def test_delete_as_anonymous_user_fails(self):
        """Usuario anónimo NO puede eliminar"""
        object_id = self.test_object.pk
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(self.model_class.objects.filter(pk=object_id).exists())
    
    def test_delete_as_regular_user_fails(self):
        """Usuario regular NO puede eliminar"""
        self.client.force_authenticate(user=self.regular_user)
        
        object_id = self.test_object.pk
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.model_class.objects.filter(pk=object_id).exists())
    
    def test_delete_as_admin_user_success(self):
        """Admin puede eliminar"""
        self.client.force_authenticate(user=self.admin_user)
        
        object_id = self.test_object.pk
        initial_count = self.model_class.objects.count()
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.model_class.objects.count(), initial_count - 1)
        self.assertFalse(self.model_class.objects.filter(pk=object_id).exists())