"""
Tests minimalistas para la funcionalidad básica de rifas.
Evalúa únicamente lo estrictamente necesario: endpoints y modelo.
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from raffle.models import Raffle
from raffleInfo.models import PrizeType, StateRaffle
from user.models import User
from userInfo.models import Gender, DocumentType
from location.models import Country, State, City


class RaffleAPITestCase(APITestCase):
    """Tests minimalistas para endpoints de rifas"""
    
    @classmethod
    def setUpTestData(cls):
        """Configuración única de datos para todos los tests"""
        # Dependencias para usuarios
        cls.gender = Gender.objects.create(gender_name="Male", gender_code="M")
        cls.document_type = DocumentType.objects.create(
            document_type_name="Cedula", document_type_code="CC"
        )
        
        # Ubicación
        cls.country = Country.objects.create(country_name="Colombia", country_code="CO")
        cls.state = State.objects.create(
            state_name="Bogotá", state_code="BOG", state_country=cls.country
        )
        cls.city = City.objects.create(
            city_name="Bogotá", city_code="BOG", city_state=cls.state
        )
        
        # Usuarios
        cls.user = User.objects.create_user(
            email='user@test.com',
            password='pass123',
            first_name='Test',
            last_name='User',
            gender=cls.gender,
            document_type=cls.document_type,
            document_number='12345678',
            city=cls.city,
        )
        
        # Datos para rifas
        cls.prize_type = PrizeType.objects.create(
            prize_type_name="Dinero", 
            prize_type_code="DIN"
        )
        cls.active_state = StateRaffle.objects.create(
            state_raffle_name="Activo", 
            state_raffle_code="ACT"
        )
        cls.inactive_state = StateRaffle.objects.create(
            state_raffle_name="Inactivo", 
            state_raffle_code="INA"
        )
        cls.cancelled_state = StateRaffle.objects.create(
            state_raffle_name="Cancelado", 
            state_raffle_code="CAN"
        )
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.future_date = timezone.now() + timedelta(days=7)
        self.valid_raffle_data = {
            'raffle_name': 'Rifa Test',
            'raffle_description': 'Descripción test',
            'raffle_draw_date': self.future_date.isoformat(),
            'raffle_minimum_numbers_sold': 10,
            'raffle_number_amount': 100,
            'raffle_number_price': '5.00',
            'raffle_price_amount': '500.00',
            'raffle_prize_type': self.prize_type.id,
        }
    
    def test_create_raffle_success(self):
        """Test crear rifa exitosamente"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/v1/raffle/create/', self.valid_raffle_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Raffle.objects.count(), 1)
    
    def test_create_raffle_unauthenticated_fails(self):
        """Test crear rifa sin autenticación falla"""
        response = self.client.post('/api/v1/raffle/create/', self.valid_raffle_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Raffle.objects.count(), 0)
    
    def test_create_raffle_invalid_data_fails(self):
        """Test crear rifa con datos inválidos falla"""
        self.client.force_authenticate(user=self.user)
        
        invalid_data = self.valid_raffle_data.copy()
        invalid_data['raffle_minimum_numbers_sold'] = 200  # Mayor que raffle_number_amount
        
        response = self.client.post('/api/v1/raffle/create/', invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Raffle.objects.count(), 0)
    
    def test_list_raffles_public_access(self):
        """Test listar rifas - acceso público"""
        # Crear rifa activa
        raffle = Raffle.objects.create(
            raffle_name='Rifa Pública',
            raffle_draw_date=self.future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        response = self.client.get('/api/v1/raffle/list/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['raffle_name'], 'Rifa Pública')
    
    def test_retrieve_raffle_detail(self):
        """Test obtener detalle de rifa específica"""
        raffle = Raffle.objects.create(
            raffle_name='Rifa Detalle',
            raffle_draw_date=self.future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/raffle/{raffle.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['raffle_name'], 'Rifa Detalle')
        self.assertEqual(response.data['id'], raffle.id)
    
    def test_update_raffle_by_creator(self):
        """Test actualizar rifa por su creador"""
        raffle = Raffle.objects.create(
            raffle_name='Rifa Original',
            raffle_draw_date=self.future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'raffle_name': 'Rifa Actualizada',
            'raffle_description': 'Nueva descripción'
        }
        
        response = self.client.patch(f'/api/v1/raffle/{raffle.id}/update/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_name, 'Rifa Actualizada')
    
    def test_update_raffle_by_non_creator_fails(self):
        """Test actualizar rifa por usuario que no es el creador falla"""
        other_user = User.objects.create_user(
            email='other@test.com',
            password='pass123',
            first_name='Other',
            last_name='User',
            gender=self.gender,
            document_type=self.document_type,
            document_number='87654321',
            city=self.city,
        )
        
        raffle = Raffle.objects.create(
            raffle_name='Rifa Ajena',
            raffle_draw_date=self.future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        self.client.force_authenticate(user=other_user)
        
        response = self.client.patch(f'/api/v1/raffle/{raffle.id}/update/', 
                                   {'raffle_name': 'Intentando cambiar'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_soft_delete_raffle(self):
        """Test soft delete de rifa"""
        raffle = Raffle.objects.create(
            raffle_name='Rifa a Eliminar',
            raffle_draw_date=self.future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.patch(f'/api/v1/raffle/{raffle.id}/delete/', {})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
    
    def test_list_user_raffles(self):
        """Test listar rifas de un usuario específico"""
        # Crear rifa del usuario
        Raffle.objects.create(
            raffle_name='Rifa Usuario',
            raffle_draw_date=self.future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/raffle/user/{self.user.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['raffle_name'], 'Rifa Usuario')


class RaffleModelTestCase(APITestCase):
    """Tests minimalistas para el modelo Raffle"""
    
    @classmethod
    def setUpTestData(cls):
        """Configuración única de datos"""
        # Dependencias
        cls.gender = Gender.objects.create(gender_name="Male", gender_code="M")
        cls.document_type = DocumentType.objects.create(
            document_type_name="Cedula", document_type_code="CC"
        )
        cls.country = Country.objects.create(country_name="Colombia", country_code="CO")
        cls.state = State.objects.create(
            state_name="Bogotá", state_code="BOG", state_country=cls.country
        )
        cls.city = City.objects.create(
            city_name="Bogotá", city_code="BOG", city_state=cls.state
        )
        cls.user = User.objects.create_user(
            email='user@test.com',
            password='pass123',
            first_name='Test',
            last_name='User',
            gender=cls.gender,
            document_type=cls.document_type,
            document_number='12345678',
            city=cls.city,
        )
        cls.prize_type = PrizeType.objects.create(
            prize_type_name="Dinero", prize_type_code="DIN"
        )
        cls.active_state = StateRaffle.objects.create(
            state_raffle_name="Activo", state_raffle_code="ACT"
        )
    
    def test_raffle_creation_assigns_default_state(self):
        """Test que la rifa asigna estado activo por defecto"""
        future_date = timezone.now() + timedelta(days=7)
        
        raffle = Raffle.objects.create(
            raffle_name='Test Rifa',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user
        )
        
        self.assertEqual(raffle.raffle_state, self.active_state)
    
    def test_raffle_validation_draw_date_after_start(self):
        """Test validación: fecha de sorteo debe ser posterior a inicio"""
        past_date = timezone.now() - timedelta(days=1)
        
        raffle = Raffle(
            raffle_name='Test Rifa',
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user
        )
        
        with self.assertRaises(Exception):
            raffle.full_clean()
    
    def test_raffle_validation_minimum_not_greater_than_total(self):
        """Test validación: mínimo no puede ser mayor que total"""
        future_date = timezone.now() + timedelta(days=7)
        
        raffle = Raffle(
            raffle_name='Test Rifa',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=150,  # Mayor que raffle_number_amount
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user
        )
        
        with self.assertRaises(Exception):
            raffle.full_clean()
    
    def test_raffle_str_method(self):
        """Test método __str__ del modelo"""
        future_date = timezone.now() + timedelta(days=7)
        
        raffle = Raffle.objects.create(
            raffle_name='Mi Rifa Test',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user
        )
        
        self.assertEqual(str(raffle), 'Mi Rifa Test')
    
    def test_raffle_is_active_for_sales_property(self):
        """Test propiedad is_active_for_sales"""
        future_date = timezone.now() + timedelta(days=7)
        
        raffle = Raffle.objects.create(
            raffle_name='Test Rifa',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        # Debe estar activa para ventas (fecha futura, estado activo, sin ganador)
        self.assertTrue(raffle.is_active_for_sales)
    
    def test_raffle_numbers_available_property(self):
        """Test propiedad numbers_available"""
        future_date = timezone.now() + timedelta(days=7)
        
        raffle = Raffle.objects.create(
            raffle_name='Test Rifa',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user
        )
        
        # Por ahora numbers_sold siempre retorna 0, así que disponibles = total
        self.assertEqual(raffle.numbers_available, 100)
    
    def test_raffle_can_execute_draw_validation(self):
        """Test método can_execute_draw básico"""
        future_date = timezone.now() + timedelta(days=7)
        
        raffle = Raffle.objects.create(
            raffle_name='Test Rifa',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_price_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        can_draw, message = raffle.can_execute_draw()
        
        # No puede sortear porque la fecha es futura
        self.assertFalse(can_draw)
        self.assertIn('programado', message.lower())