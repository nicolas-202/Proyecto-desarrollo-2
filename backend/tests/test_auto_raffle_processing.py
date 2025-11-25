"""
Tests para el sistema automático de sorteo de rifas.
Cubre signals, comando de gestión y procesamiento automático.
"""
from rest_framework.test import APITestCase
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.core.management import call_command
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from io import StringIO
import logging
from datetime import date

from raffle.models import Raffle
from raffleInfo.models import PrizeType, StateRaffle
from user.models import User
from userInfo.models import Gender, DocumentType, PaymentMethodType, PaymentMethod
from location.models import Country, State, City
from tickets.models import Ticket


class AutoRaffleProcessingTestCase(TransactionTestCase):
    """Tests para el procesamiento automático de rifas vencidas"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configurar logging para tests
        logging.disable(logging.CRITICAL)
    
    def setUp(self):
        """Configuración antes de cada test"""
        # Dependencias para usuarios
        self.gender, _ = Gender.objects.get_or_create(
            gender_name="Male", 
            defaults={"gender_code": "M"}
        )
        self.document_type, _ = DocumentType.objects.get_or_create(
            document_type_name="Cedula", 
            defaults={"document_type_code": "CC"}
        )
        
        # Ubicación
        self.country, _ = Country.objects.get_or_create(
            country_name="Colombia", 
            defaults={"country_code": "CO"}
        )
        self.state, _ = State.objects.get_or_create(
            state_name="Bogotá", 
            defaults={"state_code": "BOG", "state_country": self.country}
        )
        self.city, _ = City.objects.get_or_create(
            city_name="Bogotá", 
            defaults={"city_code": "BOG", "city_state": self.state}
        )
        
        # Usuarios
        self.user = User.objects.create_user(
            email='user@test.com',
            password='pass123',
            first_name='Test',
            last_name='User',
            gender=self.gender,
            document_type=self.document_type,
            document_number='12345678',
            city=self.city,
        )
        
        self.participant1 = User.objects.create_user(
            email='participant1@test.com',
            password='pass123',
            first_name='Participant',
            last_name='One',
            gender=self.gender,
            document_type=self.document_type,
            document_number='87654321',
            city=self.city,
        )
        
        self.participant2 = User.objects.create_user(
            email='participant2@test.com',
            password='pass123',
            first_name='Participant',
            last_name='Two',
            gender=self.gender,
            document_type=self.document_type,
            document_number='11111111',
            city=self.city,
        )
        
        # Datos para rifas
        self.prize_type, _ = PrizeType.objects.get_or_create(
            prize_type_name="Dinero",
            defaults={"prize_type_code": "DIN"}
        )
        self.active_state, _ = StateRaffle.objects.get_or_create(
            state_raffle_name="Activa",
            defaults={"state_raffle_code": "ACT"}
        )
        self.cancelled_state, _ = StateRaffle.objects.get_or_create(
            state_raffle_name="Cancelada",
            defaults={"state_raffle_code": "CAN"}
        )
        self.sorted_state, _ = StateRaffle.objects.get_or_create(
            state_raffle_name="Sorteada",
            defaults={"state_raffle_code": "SOR"}
        )        # Método de pago para tickets
        self.payment_method_type, _ = PaymentMethodType.objects.get_or_create(
            payment_method_type_name="Efectivo",
            defaults={"payment_method_type_code": "EFE"}
        )
        from datetime import date
        self.payment_method = PaymentMethod.objects.create(
            user=self.participant1,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Participant One",
            paymenth_method_card_number_hash="hashed_card_123",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="1234",
            payment_method_balance=Decimal('1000.00')
        )
        self.payment_method2 = PaymentMethod.objects.create(
            user=self.participant2,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Participant Two",
            paymenth_method_card_number_hash="hashed_card_456",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="5678",
            payment_method_balance=Decimal('1000.00')
        )
        
        # Método de pago para el organizador (self.user)
        self.organizer_payment_method = PaymentMethod.objects.create(
            user=self.user,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Test User",
            paymenth_method_card_number_hash="hashed_card_organizer",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="9999",
            payment_method_balance=Decimal('10000.00')
        )
        
        # Usuario admin y método de pago admin para cancelaciones automáticas
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass',
            first_name='Admin',
            last_name='Cuenta',
            gender=self.gender,
            document_type=self.document_type,
            document_number="0000000000",
            city=self.city,
        )
        self.admin_payment_method = PaymentMethod.objects.create(
            user=self.admin_user,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Admin Cuenta",
            paymenth_method_card_number_hash="hashed_card_admin",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="0000",
            payment_method_balance=Decimal('0.00')
        )
    
    def create_expired_raffle(self, minimum_sold=3, numbers_amount=10, days_expired=1):
        """Helper para crear rifas vencidas"""
        past_date = timezone.now() - timedelta(days=days_expired)
        start_date = past_date - timedelta(days=2)  # Fecha inicio anterior a fecha sorteo
        
        raffle = Raffle.objects.create(
            raffle_name='Rifa Test Vencida',
            raffle_description='Test rifa vencida',
            raffle_start_date=start_date,
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=minimum_sold,
            raffle_number_amount=numbers_amount,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        return raffle
    
    def test_signal_auto_cancellation_no_minimum(self):
        """Test: Signal cancela automáticamente rifa vencida sin mínimo"""
        # Crear rifa vencida sin tickets
        raffle = self.create_expired_raffle(minimum_sold=3)
        
        # Simular carga desde BD (trigger del signal post_init)
        with transaction.atomic():
            loaded_raffle = Raffle.objects.get(id=raffle.id)
            
        # Verificar que se canceló automáticamente
        loaded_raffle.refresh_from_db()
        self.assertEqual(loaded_raffle.raffle_state, self.cancelled_state)
        self.assertIsNone(loaded_raffle.raffle_winner)
    
    def test_signal_auto_draw_with_minimum(self):
        """Test: Signal sortea automáticamente rifa vencida con mínimo alcanzado"""
        # Crear rifa que aún no esté vencida
        future_date = timezone.now() + timedelta(hours=1)
        start_date = timezone.now() - timedelta(hours=1)
        
        raffle = Raffle.objects.create(
            raffle_name='Rifa Test Con Mínimo',
            raffle_start_date=start_date,
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=2,
            raffle_number_amount=5,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        
        # Vender tickets para alcanzar el mínimo
        Ticket.objects.create(
            user=self.participant1,
            raffle=raffle,
            number=1,
            payment_method=self.payment_method
        )
        Ticket.objects.create(
            user=self.participant2,
            raffle=raffle,
            number=2,
            payment_method=self.payment_method2
        )
        
        # Ahora vencer la rifa manualmente usando update (bypass validation)
        past_date = timezone.now() - timedelta(hours=2)
        start_date = past_date - timedelta(hours=1)  # Asegurar fecha inicio anterior
        Raffle.objects.filter(id=raffle.id).update(
            raffle_draw_date=past_date,
            raffle_start_date=start_date
        )
        raffle.refresh_from_db()
        
        # Simular carga desde BD
        with transaction.atomic():
            loaded_raffle = Raffle.objects.get(id=raffle.id)
            
        # Verificar que se sorteó automáticamente
        loaded_raffle.refresh_from_db()
        self.assertEqual(loaded_raffle.raffle_state, self.sorted_state)
        self.assertIsNotNone(loaded_raffle.raffle_winner)
        
        # Verificar que hay un ticket ganador
        winner_ticket = Ticket.objects.filter(raffle=raffle, is_winner=True).first()
        self.assertIsNotNone(winner_ticket)
        self.assertEqual(loaded_raffle.raffle_winner, winner_ticket.user)
    
    def test_signal_ignores_future_raffles(self):
        """Test: Signal no procesa rifas futuras"""
        # Crear rifa futura
        future_date = timezone.now() + timedelta(days=7)
        raffle = Raffle.objects.create(
            raffle_name='Rifa Futura',
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=3,
            raffle_number_amount=10,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        
        with transaction.atomic():
            loaded_raffle = Raffle.objects.get(id=raffle.id)
            
        # Verificar que no se procesó
        loaded_raffle.refresh_from_db()
        self.assertEqual(loaded_raffle.raffle_state, self.active_state)
        self.assertIsNone(loaded_raffle.raffle_winner)
    
    def test_signal_ignores_already_drawn_raffles(self):
        """Test: Signal no procesa rifas ya sorteadas"""
        raffle = self.create_expired_raffle()
        raffle.raffle_winner = self.participant1
        raffle.raffle_state = self.sorted_state
        raffle.save()
        
        original_state = raffle.raffle_state
        
        # Simular carga
        with transaction.atomic():
            loaded_raffle = Raffle.objects.get(id=raffle.id)
            
        # Verificar que no cambió
        loaded_raffle.refresh_from_db()
        self.assertEqual(loaded_raffle.raffle_state, original_state)
        self.assertEqual(loaded_raffle.raffle_winner, self.participant1)
    
    def test_signal_one_hour_delay_prevents_spam(self):
        """Test: Signal no procesa rifas vencidas hace menos de 1 hora"""
        # Crear rifa vencida hace 30 minutos
        recent_past = timezone.now() - timedelta(minutes=30)
        start_date = recent_past - timedelta(hours=1)  # Asegurar fecha inicio anterior
        
        raffle = Raffle.objects.create(
            raffle_name='Rifa Recién Vencida',
            raffle_start_date=start_date,
            raffle_draw_date=recent_past,
            raffle_minimum_numbers_sold=3,
            raffle_number_amount=10,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        
        # Simular carga desde BD
        with transaction.atomic():
            loaded_raffle = Raffle.objects.get(id=raffle.id)
            
        # Verificar que NO se procesó (muy reciente)
        loaded_raffle.refresh_from_db()
        self.assertEqual(loaded_raffle.raffle_state, self.active_state)


class ManagementCommandTestCase(TestCase):
    """Tests para el comando de gestión process_expired_raffles"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        # Crear dependencias básicas
        self.gender, _ = Gender.objects.get_or_create(
            gender_name="Male", 
            defaults={"gender_code": "M"}
        )
        self.document_type, _ = DocumentType.objects.get_or_create(
            document_type_name="Cedula", 
            defaults={"document_type_code": "CC"}
        )
        self.country = Country.objects.create(country_name="Colombia", country_code="CO")
        self.state = State.objects.create(
            state_name="Bogotá", state_code="BOG", state_country=self.country
        )
        self.city = City.objects.create(
            city_name="Bogotá", city_code="BOG", city_state=self.state
        )
        
        self.user = User.objects.create_user(
            email='user@test.com',
            password='pass123',
            first_name='Test',
            last_name='User',
            gender=self.gender,
            document_type=self.document_type,
            document_number='12345678',
            city=self.city,
        )
        
        self.prize_type = PrizeType.objects.create(
            prize_type_name="Dinero", 
            prize_type_code="DIN"
        )
        self.active_state = StateRaffle.objects.create(
            state_raffle_name="Activa", 
            state_raffle_code="ACT"
        )
        self.cancelled_state = StateRaffle.objects.create(
            state_raffle_name="Cancelada", 
            state_raffle_code="CAN"
        )
        self.payment_method_type, _ = PaymentMethodType.objects.get_or_create(
            payment_method_type_name="Efectivo",
            defaults={"payment_method_type_code": "EFE"}
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass',
            first_name='Admin',
            last_name='Cuenta',
            gender=self.gender,
            document_type=self.document_type,
            document_number="0000000000",
            city=self.city,
        )
        self.admin_payment_method = PaymentMethod.objects.create(
            user=self.admin_user,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Admin Cuenta",
            paymenth_method_card_number_hash="hashed_card_admin",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="0000",
            payment_method_balance=Decimal('0.00')
        )
        
        # Payment method para el usuario organizador
        self.organizer_payment_method = PaymentMethod.objects.create(
            user=self.user,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Test User",
            paymenth_method_card_number_hash="hashed_card_user",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="9999",
            payment_method_balance=Decimal('10000.00')
        )
    
    def test_command_dry_run_no_changes(self):
        """Test: Comando en dry-run no hace cambios reales"""
        from django.db.models.signals import post_save, post_init
        from raffle.signals import auto_process_expired_raffle, check_raffle_on_load
        from raffle.models import Raffle
        
        # Desconectar signals completamente
        post_save.disconnect(auto_process_expired_raffle, sender=Raffle)
        post_init.disconnect(check_raffle_on_load, sender=Raffle)
        
        try:
            # Crear rifa vencida
            past_date = timezone.now() - timedelta(days=2)
            start_date = past_date - timedelta(days=1)  # Fecha inicio anterior
            raffle = Raffle.objects.create(
                raffle_name='Rifa Vencida Test',
                raffle_start_date=start_date,
                raffle_draw_date=past_date,
                raffle_minimum_numbers_sold=3,
                raffle_number_amount=10,
                raffle_number_price=Decimal('10.00'),
                raffle_prize_amount=Decimal('100.00'),
                raffle_prize_type=self.prize_type,
                raffle_state=self.active_state,
                raffle_created_by=self.user,
                raffle_creator_payment_method=self.organizer_payment_method
            )
            
            # Ejecutar comando en dry-run
            out = StringIO()
            call_command('process_expired_raffles', '--dry-run', stdout=out)
            
            # Verificar que no hubo cambios
            raffle.refresh_from_db()
            self.assertEqual(raffle.raffle_state, self.active_state)
            
        finally:
            # Reconectar signals
            post_save.connect(auto_process_expired_raffle, sender=Raffle)
            post_init.connect(check_raffle_on_load, sender=Raffle)
        
        # Verificar que el output menciona que se cancelaría
        output = out.getvalue()
        self.assertIn('DRY RUN', output)
        self.assertIn('Se cancelaría', output)
    
    def test_command_real_execution_makes_changes(self):
        """Test: Comando real hace cambios efectivos"""
        # Crear rifa vencida sin mínimo
        past_date = timezone.now() - timedelta(days=2)
        start_date = past_date - timedelta(days=1)  # Fecha inicio anterior
        raffle = Raffle.objects.create(
            raffle_name='Rifa Vencida Test',
            raffle_start_date=start_date,
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=3,
            raffle_number_amount=10,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        
        # Ejecutar comando real
        out = StringIO()
        call_command('process_expired_raffles', stdout=out)
        
        # Verificar que se canceló
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('CANCELADA', output)
        self.assertIn('completado exitosamente', output)
    
    def test_command_force_flag_processes_recent(self):
        """Test: Flag --force procesa rifas recién vencidas"""
        # Crear rifa vencida hace 30 minutos
        recent_past = timezone.now() - timedelta(minutes=30)
        start_date = recent_past - timedelta(hours=2)  # Fecha inicio anterior
        raffle = Raffle.objects.create(
            raffle_name='Rifa Recién Vencida',
            raffle_start_date=start_date,
            raffle_draw_date=recent_past,
            raffle_minimum_numbers_sold=3,
            raffle_number_amount=10,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        
        # Sin --force no debería procesar
        out1 = StringIO()
        call_command('process_expired_raffles', '--dry-run', stdout=out1)
        output1 = out1.getvalue()
        self.assertIn('Rifas vencidas encontradas: 0', output1)
        
        # Con --force sí debería procesar
        out2 = StringIO()
        call_command('process_expired_raffles', '--dry-run', '--force', stdout=out2)
        output2 = out2.getvalue()
        self.assertIn('Rifas vencidas encontradas: 1', output2)
    
    def test_command_handles_missing_cancelled_state(self):
        """Test: Comando maneja correctamente estado cancelado faltante"""
        # Eliminar estado cancelado
        StateRaffle.objects.filter(state_raffle_code='CAN').delete()
        
        # Crear rifa vencida
        past_date = timezone.now() - timedelta(days=2)
        start_date = past_date - timedelta(days=1)  # Fecha inicio anterior
        Raffle.objects.create(
            raffle_name='Rifa Test',
            raffle_start_date=start_date,
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=3,
            raffle_number_amount=10,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        
        # Ejecutar comando debería fallar con error descriptivo
        with self.assertRaises(Exception):  # CommandError o SystemExit
            out = StringIO()
            call_command('process_expired_raffles', '--dry-run', stdout=out)


class IntegrationTestCase(APITestCase):
    """Tests de integración para flujos completos"""
    
    def setUp(self):
        """Configuración completa"""
        # Crear todos los datos necesarios
        self.gender, _ = Gender.objects.get_or_create(
            gender_name="Male", 
            defaults={"gender_code": "M"}
        )
        self.document_type, _ = DocumentType.objects.get_or_create(
            document_type_name="Cedula", 
            defaults={"document_type_code": "CC"}
        )
        self.country = Country.objects.create(country_name="Colombia", country_code="CO")
        self.state = State.objects.create(
            state_name="Bogotá", state_code="BOG", state_country=self.country
        )
        self.city = City.objects.create(
            city_name="Bogotá", city_code="BOG", city_state=self.state
        )
        
        self.organizer = User.objects.create_user(
            email='organizer@test.com',
            password='pass123',
            first_name='Organizer',
            last_name='User',
            gender=self.gender,
            document_type=self.document_type,
            document_number='12345678',
            city=self.city,
            is_staff=True
        )
        
        self.participant = User.objects.create_user(
            email='participant@test.com',
            password='pass123',
            first_name='Participant',
            last_name='User',
            gender=self.gender,
            document_type=self.document_type,
            document_number='87654321',
            city=self.city,
        )
        
        # Payment methods
        self.payment_method_type, _ = PaymentMethodType.objects.get_or_create(
            payment_method_type_name="Efectivo",
            defaults={"payment_method_type_code": "EFE"}
        )
        
        self.organizer_payment_method = PaymentMethod.objects.create(
            user=self.organizer,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Organizer User",
            paymenth_method_card_number_hash="hashed_card_organizer",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="9999",
            payment_method_balance=Decimal('10000.00')
        )
        
        self.prize_type = PrizeType.objects.create(
            prize_type_name="Dinero", 
            prize_type_code="DIN"
        )
        self.active_state = StateRaffle.objects.create(
            state_raffle_name="Activa", 
            state_raffle_code="ACT"
        )
        self.cancelled_state = StateRaffle.objects.create(
            state_raffle_name="Cancelada", 
            state_raffle_code="CAN"
        )
        self.sorted_state = StateRaffle.objects.create(
            state_raffle_name="Sorteada", 
            state_raffle_code="SOR"
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass',
            first_name='Admin',
            last_name='Cuenta',
            gender=self.gender,
            document_type=self.document_type,
            document_number="0000000000",
            city=self.city,
        )
        self.admin_payment_method = PaymentMethod.objects.create(
            user=self.admin_user,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Admin Cuenta",
            paymenth_method_card_number_hash="hashed_card_admin",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="0000",
            payment_method_balance=Decimal('0.00')
        )
    
    def test_full_workflow_automatic_cancellation(self):
        """Test: Flujo completo de cancelación automática"""
        # 1. Crear rifa con fecha futura
        future_date = timezone.now() + timedelta(hours=1)
        raffle_data = {
            'raffle_name': 'Rifa Test Automática',
            'raffle_description': 'Test completo',
            'raffle_draw_date': future_date.isoformat(),
            'raffle_minimum_numbers_sold': 5,
            'raffle_number_amount': 10,
            'raffle_number_price': '10.00',
            'raffle_prize_amount': '100.00',
            'raffle_prize_type': self.prize_type.id,
            'raffle_creator_payment_method': self.organizer_payment_method.id,
        }
        
        self.client.force_authenticate(user=self.organizer)
        response = self.client.post('/api/v1/raffle/create/', raffle_data)
        self.assertEqual(response.status_code, 201)
        
        # El response puede tener diferentes estructuras según el serializer
        raffle_id = response.data.get('id') or response.data.get('raffle_id') or Raffle.objects.last().id
        
        # 2. Verificar que la rifa está activa
        raffle = Raffle.objects.get(id=raffle_id)
        self.assertEqual(raffle.raffle_state, self.active_state)
        # 3. Simular que el tiempo pasó (cambiar fecha manualmente)
        past_date = timezone.now() - timedelta(hours=2)
        start_date = past_date - timedelta(hours=1)
        Raffle.objects.filter(id=raffle_id).update(
            raffle_draw_date=past_date,
            raffle_start_date=start_date
        )
        # 4. Recargar la rifa para disparar el signal
        with transaction.atomic():
            loaded_raffle = Raffle.objects.get(id=raffle_id)
        loaded_raffle.refresh_from_db()
        self.assertEqual(loaded_raffle.raffle_state, self.cancelled_state)
        self.assertIsNone(loaded_raffle.raffle_winner)
    
    def test_full_workflow_with_manual_command(self):
        """Test: Flujo usando comando manual"""
        # Crear múltiples rifas vencidas
        past_date = timezone.now() - timedelta(days=1)
        
        start_date = past_date - timedelta(days=1)  # Fecha inicio anterior
        for i in range(3):
            Raffle.objects.create(
                raffle_name=f'Rifa Test {i+1}',
                raffle_start_date=start_date,
                raffle_draw_date=past_date,
                raffle_minimum_numbers_sold=5,
                raffle_number_amount=10,
                raffle_number_price=Decimal('10.00'),
                raffle_prize_amount=Decimal('100.00'),
                raffle_prize_type=self.prize_type,
                raffle_state=self.active_state,
                raffle_created_by=self.organizer,
                raffle_creator_payment_method=self.organizer_payment_method
            )
        
        # Ejecutar comando
        out = StringIO()
        call_command('process_expired_raffles', stdout=out)
        
        # Verificar que todas se cancelaron
        cancelled_count = Raffle.objects.filter(
            raffle_state=self.cancelled_state
        ).count()
        self.assertEqual(cancelled_count, 3)
        
        output = out.getvalue()
        self.assertIn('Rifas canceladas: 3', output)
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Re-habilitar logging después de los tests
        logging.disable(logging.NOTSET)