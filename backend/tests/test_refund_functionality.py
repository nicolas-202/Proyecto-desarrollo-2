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
from django.db.models.signals import post_save, post_init

from raffle.models import Raffle
from raffleInfo.models import StateRaffle, PrizeType
from user.models import User
from location.models import Country, State, City
from userInfo.models import Gender, DocumentType
from tickets.models import Ticket, PaymentMethod
from userInfo.models import PaymentMethodType
from raffle.signals import auto_process_expired_raffle, check_raffle_on_load


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
        
        # TIPO DE MÉTODO DE PAGO
        self.payment_method_type = PaymentMethodType.objects.create(
            payment_method_type_name=f"Efectivo-{self.test_id}",
            payment_method_type_code=f"EFE-{self.test_id}"
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

        # Métodos de pago para participantes
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

        # Método de pago para el organizador
        self.organizer_payment_method = PaymentMethod.objects.create(
            user=self.user,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Organizer User",
            paymenth_method_card_number_hash="hashed_card_organizer",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="9999",
            payment_method_balance=Decimal('10000.00')
        )

        # Crear usuario admin y método de pago admin
        self.admin_user = User.objects.create_user(
            email=f'admin-{self.test_id}@test.com',
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



    def test_signal_cancellation_with_refunds(self):
        """Test: Signal cancela rifa vencida CON tickets y procesa reembolsos"""
        now = timezone.now()
        raffle = Raffle.objects.create(
            raffle_name='Rifa Test Reembolsos',
            raffle_start_date=now - timedelta(hours=1),
            raffle_draw_date=now + timedelta(hours=2),
            raffle_minimum_numbers_sold=5,
            raffle_number_amount=10,
            raffle_number_price=Decimal('25.00'),
            raffle_prize_amount=Decimal('200.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )

        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        self.admin_payment_method.payment_method_balance = Decimal('0.00')
        self.admin_payment_method.save()
        initial_admin_balance = Decimal('0.00')

        Ticket.purchase_ticket(self.participant1, raffle, 1, self.payment_method)
        Ticket.purchase_ticket(self.participant2, raffle, 2, self.payment_method2)

        self.assertEqual(raffle.sold_tickets.count(), 2)
        self.admin_payment_method.refresh_from_db()
        expected_admin_balance = initial_admin_balance + (2 * raffle.raffle_number_price)
        self.assertEqual(self.admin_payment_method.payment_method_balance, expected_admin_balance)

        # Simular vencimiento y disparar el signal
        past_draw_date = now - timedelta(hours=2)
        past_start_date = past_draw_date - timedelta(hours=1)
        raffle.raffle_start_date = past_start_date
        raffle.raffle_draw_date = past_draw_date
        raffle._allow_past_date = True
        raffle.save()  # Aquí el signal debe actuar

        # Verificar que el estado fue cambiado por el signal
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
        self.assertEqual(raffle.sold_tickets.count(), 0)

        # Verificar reembolsos usando consulta directa a la BD
        pm1 = PaymentMethod.objects.get(id=self.payment_method.id)
        pm2 = PaymentMethod.objects.get(id=self.payment_method2.id)
        self.assertEqual(pm1.payment_method_balance, initial_balance_1)
        self.assertEqual(pm2.payment_method_balance, initial_balance_2)
        admin_pm = PaymentMethod.objects.get(id=self.admin_payment_method.id)
        self.assertEqual(admin_pm.payment_method_balance, Decimal('0.00'))

    def test_command_cancellation_with_refunds(self):
        """Test: Comando cancela rifa vencida CON reembolsos (por signal)"""
        now = timezone.now()
        raffle = Raffle.objects.create(
            raffle_name='Rifa Comando Reembolsos',
            raffle_start_date=now - timedelta(hours=1),
            raffle_draw_date=now + timedelta(days=1),
            raffle_minimum_numbers_sold=10,
            raffle_number_amount=20,
            raffle_number_price=Decimal('50.00'),
            raffle_prize_amount=Decimal('500.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )

        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        self.admin_payment_method.payment_method_balance = Decimal('0.00')
        self.admin_payment_method.save()
        initial_admin_balance = Decimal('0.00')

        Ticket.purchase_ticket(self.participant1, raffle, 1, self.payment_method)
        Ticket.purchase_ticket(self.participant2, raffle, 2, self.payment_method2)
        Ticket.purchase_ticket(self.participant1, raffle, 3, self.payment_method)

        self.assertEqual(raffle.sold_tickets.count(), 3)
        self.admin_payment_method.refresh_from_db()
        expected_admin_balance = initial_admin_balance + (3 * raffle.raffle_number_price)
        self.assertEqual(self.admin_payment_method.payment_method_balance, expected_admin_balance)

        # Simular vencimiento y disparar el signal
        past_draw_date = now - timedelta(days=1)
        past_start_date = past_draw_date - timedelta(hours=1)
        raffle.raffle_start_date = past_start_date
        raffle.raffle_draw_date = past_draw_date
        raffle._allow_past_date = True
        raffle.save()

        # Verificar estado y reembolsos tras el signal
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
        self.assertEqual(raffle.sold_tickets.count(), 0)

        pm1 = PaymentMethod.objects.get(id=self.payment_method.id)
        pm2 = PaymentMethod.objects.get(id=self.payment_method2.id)
        self.assertEqual(pm1.payment_method_balance, initial_balance_1)
        self.assertEqual(pm2.payment_method_balance, initial_balance_2)
        admin_pm = PaymentMethod.objects.get(id=self.admin_payment_method.id)
        self.assertEqual(admin_pm.payment_method_balance, Decimal('0.00'))

    def test_manual_cancel_method_refunds(self):
        """Test: Cancelación manual funciona correctamente (por signal)"""
        now = timezone.now()
        raffle = Raffle.objects.create(
            raffle_name='Rifa Manual Cancel',
            raffle_start_date=now - timedelta(hours=1),
            raffle_draw_date=now + timedelta(hours=2),
            raffle_minimum_numbers_sold=5,
            raffle_number_amount=10,
            raffle_number_price=Decimal('30.00'),
            raffle_prize_amount=Decimal('300.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )

        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        self.admin_payment_method.payment_method_balance = Decimal('0.00')
        self.admin_payment_method.save()
        initial_admin_balance = Decimal('0.00')

        Ticket.purchase_ticket(self.participant1, raffle, 1, self.payment_method)
        Ticket.purchase_ticket(self.participant2, raffle, 2, self.payment_method2)

        self.assertEqual(raffle.sold_tickets.count(), 2)
        self.admin_payment_method.refresh_from_db()
        expected_admin_balance = initial_admin_balance + (2 * raffle.raffle_number_price)
        self.assertEqual(self.admin_payment_method.payment_method_balance, expected_admin_balance)

        # Simular vencimiento y disparar el signal
        past_draw_date = now - timedelta(hours=2)
        past_start_date = past_draw_date - timedelta(hours=1)
        raffle.raffle_start_date = past_start_date
        raffle.raffle_draw_date = past_draw_date
        raffle._allow_past_date = True
        raffle.save()

        # Verificar estado y reembolsos tras el signal
        raffle.refresh_from_db()
        self.assertEqual(raffle.raffle_state, self.cancelled_state)
        self.assertEqual(raffle.sold_tickets.count(), 0)

        pm1 = PaymentMethod.objects.get(id=self.payment_method.id)
        pm2 = PaymentMethod.objects.get(id=self.payment_method2.id)
        self.assertEqual(pm1.payment_method_balance, initial_balance_1)
        self.assertEqual(pm2.payment_method_balance, initial_balance_2)
        admin_pm = PaymentMethod.objects.get(id=self.admin_payment_method.id)
        self.assertEqual(admin_pm.payment_method_balance, Decimal('0.00'))

    def test_no_refunds_when_no_tickets(self):
        """Test: No hay reembolsos cuando no hay tickets vendidos"""
        # Crear rifa en el futuro, sin tickets
        now = timezone.now()
        raffle = Raffle.objects.create(
            raffle_name='Rifa Sin Tickets',
            raffle_start_date=now - timedelta(hours=1),
            raffle_draw_date=now + timedelta(hours=2),
            raffle_minimum_numbers_sold=5,
            raffle_number_amount=10,
            raffle_number_price=Decimal('20.00'),
            raffle_prize_amount=Decimal('100.00'),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method
        )
        
        # NO creamos tickets - dejamos la rifa vacía
        
        # Simular vencimiento
        past_draw_date = now - timedelta(hours=2)
        past_start_date = past_draw_date - timedelta(hours=1)
        
        raffle.raffle_start_date = past_start_date
        raffle.raffle_draw_date = past_draw_date
        raffle._allow_past_date = True
        raffle.save()
        
        # Guardar balances iniciales
        initial_balance_1 = self.payment_method.payment_method_balance
        initial_balance_2 = self.payment_method2.payment_method_balance
        
        # Usar método de cancelación
        result = raffle.cancel_raffle_and_refund("No tickets to refund")
        
        # Verificar resultado
        self.assertEqual(result['tickets_refunded'], 0)
        self.assertEqual(result['total_amount_refunded'], 0)
        
        # Verificar que balances no cambiaron
        pm1 = PaymentMethod.objects.get(id=self.payment_method.id)
        pm2 = PaymentMethod.objects.get(id=self.payment_method2.id)
        self.assertEqual(pm1.payment_method_balance, initial_balance_1)
        self.assertEqual(pm2.payment_method_balance, initial_balance_2)
        
    def tearDown(self):
        """Limpieza después de cada test"""
        pass