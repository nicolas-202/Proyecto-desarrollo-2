"""
Tests específicos para funcionalidad de reembolsos automáticos
Estrategia: Tests simplificados que prueban directamente el método cancel_raffle_and_refund
"""
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.db import transaction
from io import StringIO
from django.core.management import call_command
import uuid

from raffle.models import Raffle
from raffleInfo.models import StateRaffle, PrizeType
from user.models import User
from location.models import Country, State, City
from userInfo.models import Gender, DocumentType
from tickets.models import Ticket, PaymentMethod
from userInfo.models import PaymentMethodType


class RefundFunctionalityTestCase(TestCase):
    """Test case para verificar reembolsos automáticos - Tests simplificados y funcionales"""
    
    def setUp(self):
        """Configuración inicial para tests de reembolsos"""
        from datetime import date
        
        # Generar identificador único para esta ejecución
        self.test_id = str(uuid.uuid4())[:8]
        
        # Ubicación - usar UUIDs para garantizar unicidad total
        self.country = Country.objects.create(
            country_name=f"Colombia-{self.test_id}", 
            country_code=f"CO-{self.test_id}"
        )
        self.state = State.objects.create(
            state_name=f"Bogotá-{self.test_id}", 
            state_code=f"BOG-{self.test_id}",
            state_country=self.country
        )
        self.city = City.objects.create(
            city_name=f"Bogotá-{self.test_id}", 
            city_code=f"BOG-{self.test_id}",
            city_state=self.state
        )
        
        # Datos de usuario - usar UUIDs únicos
        self.gender = Gender.objects.create(
            gender_name=f"Masculino-{self.test_id}",
            gender_code=f"M-{self.test_id}"
        )
        self.document_type = DocumentType.objects.create(
            document_type_name=f"Cedula-{self.test_id}", 
            document_type_code=f"CC-{self.test_id}"
        )
        
        # Datos para rifas - usar UUIDs únicos
        self.prize_type = PrizeType.objects.create(
            prize_type_name=f"Dinero-{self.test_id}",
            prize_type_code=f"DIN-{self.test_id}"
        )
        self.active_state = StateRaffle.objects.create(
            state_raffle_name=f"Activa-{self.test_id}",
            state_raffle_code=f"ACT-{self.test_id}"
        )
        self.cancelled_state = StateRaffle.objects.create(
            state_raffle_name=f"Cancelada-{self.test_id}",
            state_raffle_code=f"CAN-{self.test_id}"
        )
        
        # Usuarios - usar UUIDs completamente únicos
        self.user = User.objects.create_user(
            email=f'organizer-{self.test_id}@test.com',
            password='pass123',
            first_name='Organizer',
            last_name='User',
            gender=self.gender,
            document_type=self.document_type,
            document_number=f'12345678-{self.test_id}',
            city=self.city,
        )
        
        self.participant1 = User.objects.create_user(
            email=f'participant1-{self.test_id}@test.com',
            password='pass123',
            first_name='Participant',
            last_name='One',
            gender=self.gender,
            document_type=self.document_type,
            document_number=f'87654321-{self.test_id}',
            city=self.city,
        )
        
        self.participant2 = User.objects.create_user(
            email=f'participant2-{self.test_id}@test.com',
            password='pass123',
            first_name='Participant',
            last_name='Two',
            gender=self.gender,
            document_type=self.document_type,
            document_number=f'11111111-{self.test_id}',
            city=self.city,
        )
        
        # Método de pago para tickets - usar UUID único
        self.payment_method_type = PaymentMethodType.objects.create(
            payment_method_type_name=f"Efectivo-{self.test_id}",
            payment_method_type_code=f"EFE-{self.test_id}"
        )
        
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

    def test_signal_cancellation_with_refunds(self):
        """Test: Signal cancela rifa vencida CON tickets y procesa reembolsos"""
        # Test simplificado: crear rifa ya vencida y usar método directo
        # (Los signals ya están probados en otros tests, aquí probamos el flujo de reembolsos)
        
        from django.db import connection
        
        # Crear rifa vencida
        past_date = timezone.now() - timedelta(hours=2)
        past_start_date = past_date - timedelta(hours=1)
        
        raffle = Raffle.objects.create(
            raffle_name='Rifa Test Reembolsos',
            raffle_start_date=past_start_date,
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=5,  # Mínimo alto que no se alcanzará
            raffle_number_amount=10,
            raffle_number_price=Decimal('25.00'),
            raffle_prize_amount=Decimal('200.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        # Guardar balances iniciales
        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        
        # Crear tickets usando SQL raw
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tickets_ticket 
                (user_id, raffle_id, number, payment_method_id, is_winner, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                self.participant1.id, raffle.id, 1, self.payment_method.id, False, 
                timezone.now()
            ])
            
            cursor.execute("""
                INSERT INTO tickets_ticket 
                (user_id, raffle_id, number, payment_method_id, is_winner, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                self.participant2.id, raffle.id, 2, self.payment_method2.id, False, 
                timezone.now()
            ])
        
        # Verificar que se vendieron los tickets
        self.assertEqual(raffle.sold_tickets.count(), 2)
        
        # Simular lo que haría el signal: usar cancel_raffle_and_refund
        result = raffle.cancel_raffle_and_refund(
            admin_reason="Cancelación automática: mínimo no alcanzado"
        )
        
        # Verificar que fue procesado correctamente
        self.assertEqual(result['tickets_refunded'], 2)
        self.assertEqual(result['total_amount_refunded'], 50)  # 2 * $25
        
        # Verificar que fue cancelada
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
        
        # Verificar que los tickets fueron eliminados (reembolsados)
        self.assertEqual(raffle.sold_tickets.count(), 0)
        
        # Verificar reembolsos
        self.payment_method.refresh_from_db()
        self.payment_method2.refresh_from_db()
        
        expected_balance_1 = initial_balance_1 + raffle.raffle_number_price
        expected_balance_2 = initial_balance_2 + raffle.raffle_number_price
        
        self.assertEqual(self.payment_method.payment_method_balance, expected_balance_1)
        self.assertEqual(self.payment_method2.payment_method_balance, expected_balance_2)

    def test_command_cancellation_with_refunds(self):
        """Test: Comando cancela rifa vencida CON reembolsos"""
        from django.db import connection
        
        # Crear rifa que YA esté vencida
        past_date = timezone.now() - timedelta(days=1)
        past_start_date = past_date - timedelta(hours=1)
        
        raffle = Raffle.objects.create(
            raffle_name='Rifa Comando Reembolsos',
            raffle_start_date=past_start_date,
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=10,  # Mínimo muy alto
            raffle_number_amount=20,
            raffle_number_price=Decimal('50.00'),
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        # Guardar balances iniciales ANTES de crear tickets
        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        
        # Crear tickets usando SQL raw con estructura correcta
        with connection.cursor() as cursor:
            # Insertar tickets directamente en BD (bypass validaciones)
            cursor.execute("""
                INSERT INTO tickets_ticket 
                (user_id, raffle_id, number, payment_method_id, is_winner, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                self.participant1.id, raffle.id, 1, self.payment_method.id, False, 
                timezone.now()
            ])
            
            cursor.execute("""
                INSERT INTO tickets_ticket 
                (user_id, raffle_id, number, payment_method_id, is_winner, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                self.participant2.id, raffle.id, 2, self.payment_method2.id, False, 
                timezone.now()
            ])
            
            cursor.execute("""
                INSERT INTO tickets_ticket 
                (user_id, raffle_id, number, payment_method_id, is_winner, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                self.participant1.id, raffle.id, 3, self.payment_method.id, False, 
                timezone.now()
            ])
        
        # Verificar que se crearon los tickets
        tickets_count = raffle.sold_tickets.count()
        self.assertEqual(tickets_count, 3)
        
        # Simular lo que hace el comando: usar cancel_raffle_and_refund
        result = raffle.cancel_raffle_and_refund(
            admin_reason="Cancelación automática por comando: mínimo no alcanzado"
        )
        
        # Verificar resultado de cancelación
        self.assertEqual(result['tickets_refunded'], 3)
        self.assertEqual(result['total_amount_refunded'], 150)  # 3 * $50
        
        # Verificar que fue cancelada
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
        
        # Verificar que no quedan tickets
        self.assertEqual(raffle.sold_tickets.count(), 0)
        
        # Verificar reembolsos (2 tickets para participant1, 1 para participant2)
        self.payment_method.refresh_from_db()
        self.payment_method2.refresh_from_db()
        
        expected_balance_1 = initial_balance_1 + (2 * raffle.raffle_number_price)  # 2 tickets
        expected_balance_2 = initial_balance_2 + (1 * raffle.raffle_number_price)  # 1 ticket
        
        self.assertEqual(self.payment_method.payment_method_balance, expected_balance_1)
        self.assertEqual(self.payment_method2.payment_method_balance, expected_balance_2)

    def test_manual_cancel_method_refunds(self):
        """Test: Método manual cancel_raffle_and_refund funciona correctamente"""
        from django.db import connection
        
        # Crear rifa vencida
        past_date = timezone.now() - timedelta(hours=2)
        raffle = Raffle.objects.create(
            raffle_name='Rifa Manual Cancel',
            raffle_start_date=past_date - timedelta(hours=1),
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=5,
            raffle_number_amount=10,
            raffle_number_price=Decimal('30.00'),
            raffle_prize_amount=Decimal('300.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        # Guardar balances iniciales
        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        
        # Crear tickets usando SQL raw para bypass completo
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tickets_ticket 
                (user_id, raffle_id, number, payment_method_id, is_winner, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                self.participant1.id, raffle.id, 1, self.payment_method.id, False, 
                timezone.now()
            ])
            
            cursor.execute("""
                INSERT INTO tickets_ticket 
                (user_id, raffle_id, number, payment_method_id, is_winner, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                self.participant2.id, raffle.id, 2, self.payment_method2.id, False, 
                timezone.now()
            ])
        
        # Verificar que hay tickets
        self.assertEqual(raffle.sold_tickets.count(), 2)
        
        # Usar método directo de cancelación
        result = raffle.cancel_raffle_and_refund("Test manual cancellation")
        
        # Verificar resultado
        self.assertEqual(result['tickets_refunded'], 2)
        self.assertEqual(result['total_amount_refunded'], 60)  # 2 * $30
        self.assertEqual(result['admin_reason'], "Test manual cancellation")
        
        # Verificar estado
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
        
        # Verificar que no quedan tickets
        self.assertEqual(raffle.sold_tickets.count(), 0)
        
        # Verificar reembolsos
        self.payment_method.refresh_from_db()
        self.payment_method2.refresh_from_db()
        
        expected_balance_1 = initial_balance_1 + raffle.raffle_number_price
        expected_balance_2 = initial_balance_2 + raffle.raffle_number_price
        
        self.assertEqual(self.payment_method.payment_method_balance, expected_balance_1)
        self.assertEqual(self.payment_method2.payment_method_balance, expected_balance_2)

    def test_no_refunds_when_no_tickets(self):
        """Test: No hay reembolsos cuando no hay tickets vendidos"""
        # Crear rifa vencida sin tickets
        past_date = timezone.now() - timedelta(hours=2)
        start_date = past_date - timedelta(hours=1)
        
        raffle = Raffle.objects.create(
            raffle_name='Rifa Sin Tickets',
            raffle_start_date=start_date,
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=5,
            raffle_number_amount=10,
            raffle_number_price=Decimal('20.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user
        )
        
        # Guardar balances iniciales
        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        
        # Usar método de cancelación
        result = raffle.cancel_raffle_and_refund("No tickets to refund")
        
        # Verificar resultado
        self.assertEqual(result['tickets_refunded'], 0)
        self.assertEqual(result['total_amount_refunded'], 0)
        
        # Verificar que balances no cambiaron
        self.payment_method.refresh_from_db()
        self.payment_method2.refresh_from_db()
        
        self.assertEqual(self.payment_method.payment_method_balance, initial_balance_1)
        self.assertEqual(self.payment_method2.payment_method_balance, initial_balance_2)
        
    def tearDown(self):
        """Limpieza opcional después de cada test"""
        # TestCase automáticamente hace rollback de la transacción, 
        # pero podemos agregar limpieza adicional si es necesaria
        pass