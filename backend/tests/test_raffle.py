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
from userInfo.models import Gender, DocumentType, PaymentMethodType, PaymentMethod
from location.models import Country, State, City
from datetime import datetime


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
        
        # PaymentMethod para el usuario
        cls.payment_method_type = PaymentMethodType.objects.create(
            payment_method_type_name="Cuenta de Ahorros",
            payment_method_type_code="SA"
        )
        cls.payment_method = PaymentMethod.objects.create(
            payment_method_type=cls.payment_method_type,
            user=cls.user,
            paymenth_method_holder_name=f"{cls.user.first_name} {cls.user.last_name}",
            paymenth_method_card_number_hash="test_hash_123",
            paymenth_method_expiration_date=datetime.now().date() + timedelta(days=365),
            last_digits="1234",
            payment_method_balance=10000000.00
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
            'raffle_prize_amount': '500.00',
            'raffle_prize_type': self.prize_type.id,
            'raffle_creator_payment_method': self.payment_method.id,
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
        )
        
        self.client.force_authenticate(user=other_user)
        
        response = self.client.patch(f'/api/v1/raffle/{raffle.id}/update/', 
                                    {'raffle_name': 'Intentando cambiar'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_user_raffles(self):
        """Test listar rifas de un usuario específico"""
        # Crear rifa del usuario
        Raffle.objects.create(
            raffle_name='Rifa Usuario',
            raffle_draw_date=self.future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
        )
        
        response = self.client.get(f'/api/v1/raffle/user/{self.user.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['raffle_name'], 'Rifa Usuario')


class RaffleModelTestCase(APITestCase):
    def test_soft_delete_and_refund_by_organizer(self):
        """Test: El organizador puede cancelar la rifa y se procesan reembolsos"""
        future_date = timezone.now() + timedelta(days=7)
        raffle = Raffle.objects.create(
            raffle_name='Rifa Cancelable',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
        )

        # Simular usuario admin y método de pago admin
        from user.models import User
        from userInfo.models import PaymentMethod, PaymentMethodType
        admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass',
            first_name='Admin',
            last_name='Cuenta',
            gender=self.gender,
            document_type=self.document_type,
            document_number="0000000000",
            city=self.city,
        )
        payment_type = PaymentMethodType.objects.create(
            payment_method_type_name="Efectivo",
            payment_method_type_code="EFE"
        )
        admin_payment = PaymentMethod.objects.create(
            user=admin_user,
            payment_method_type=payment_type,
            paymenth_method_holder_name="Admin Cuenta",
            paymenth_method_card_number_hash="hashed_card_admin",
            paymenth_method_expiration_date=(timezone.now() + timedelta(days=365)).date(),
            last_digits="0000",
            payment_method_balance=Decimal('1000.00'),
            payment_method_is_active=True
        )

        # Simular ticket vendido
        from tickets.models import Ticket
        user_payment = PaymentMethod.objects.create(
            user=self.user,
            payment_method_type=payment_type,
            paymenth_method_holder_name="Test User",
            paymenth_method_card_number_hash="hashed_card_user",
            paymenth_method_expiration_date=(timezone.now() + timedelta(days=365)).date(),
            last_digits="1234",
            payment_method_balance=Decimal('0.00'),
            payment_method_is_active=True
        )
        ticket = Ticket.objects.create(
            user=self.user,
            raffle=raffle,
            number=1,
            payment_method=user_payment
        )

        # Ejecutar soft_delete_and_refund por el organizador (solo una vez)
        result = raffle.soft_delete_and_refund(self.user)
        raffle.refresh_from_db()
        from raffleInfo.models import StateRaffle
        cancelled_state = StateRaffle.objects.filter(state_raffle_code='CAN').first()
        self.assertIsNotNone(cancelled_state)
        self.assertEqual(raffle.raffle_state.id, cancelled_state.id)
        self.assertEqual(result['tickets_refunded'], 1)
        self.assertEqual(result['total_amount_refunded'], 5.0)
        self.assertEqual(result['organizer'], self.user.email)

    def test_soft_delete_and_refund_by_non_organizer_fails(self):
        """Test: Solo el organizador puede cancelar la rifa"""
        future_date = timezone.now() + timedelta(days=7)
        raffle = Raffle.objects.create(
            raffle_name='Rifa No Cancelable',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=100,
            raffle_number_price=Decimal('5.00'),
                raffle_prize_amount=Decimal('500.00'),
                raffle_prize_type=self.prize_type,
                raffle_state=self.active_state,
                raffle_created_by=self.user,
                raffle_creator_payment_method=self.payment_method
            )
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
        with self.assertRaises(Exception):
                raffle.soft_delete_and_refund(other_user)
    

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
        
        # PaymentMethod para el usuario
        from userInfo.models import PaymentMethodType, PaymentMethod
        cls.payment_method_type = PaymentMethodType.objects.create(
            payment_method_type_name="Cuenta de Ahorros",
            payment_method_type_code="SA"
        )
        cls.payment_method = PaymentMethod.objects.create(
            payment_method_type=cls.payment_method_type,
            user=cls.user,
            paymenth_method_holder_name=f"{cls.user.first_name} {cls.user.last_name}",
            paymenth_method_card_number_hash="test_hash_456",
            paymenth_method_expiration_date=datetime.now().date() + timedelta(days=365),
            last_digits="5678",
            payment_method_balance=10000000.00
        )
        
        cls.prize_type = PrizeType.objects.create(
            prize_type_name="Dinero", prize_type_code="DIN"
        )
        cls.active_state = StateRaffle.objects.create(
            state_raffle_name="Activo", state_raffle_code="ACT"
        )
        # Crear estado cancelado para los tests
        cls.cancelled_state = StateRaffle.objects.create(
            state_raffle_name="Cancelado", state_raffle_code="CAN"
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
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
            raffle_prize_amount=Decimal('500.00'),
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
            raffle_prize_amount=Decimal('500.00'),
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
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
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.payment_method
        )
        
        can_draw, message = raffle.can_execute_draw()
        
        # No puede sortear porque la fecha es futura
        self.assertFalse(can_draw)
        self.assertIn('mínimo', message.lower())