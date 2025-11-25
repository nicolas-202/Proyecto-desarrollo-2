"""
Tests optimizados para el sistema de tickets y rifas
Sigue la estructura estándar del proyecto con APITestCase y setUpTestData
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError

from tickets.models import Ticket
from raffle.models import Raffle
from userInfo.models import PaymentMethod, PaymentMethodType, Gender, DocumentType
from raffleInfo.models import PrizeType, StateRaffle
from location.models import Country, State, City
from user.models import User


class TicketSystemTestCase(APITestCase):
    """
    Tests optimizados para el sistema completo de tickets y rifas
    Enfoque en funcionalidades críticas con datos compartidos
    """
    
    @classmethod
    def setUpTestData(cls):
        """Crear datos comunes para todos los tests"""
        
        # === DATOS GEOGRÁFICOS ===
        cls.country = Country.objects.create(
            country_name="Colombia",
            country_code="CO"
        )
        cls.state = State.objects.create(
            state_name="TestState",
            state_country=cls.country,
            state_code="TS"
        )
        cls.city = City.objects.create(
            city_name="TestCity",
            city_state=cls.state,
            city_code="TC"
        )
        
        # === DATOS BASE ===
        cls.gender = Gender.objects.create(
            gender_name="Masculino",
            gender_code="M"
        )
        cls.document_type = DocumentType.objects.create(
            document_type_name="Cedula",
            document_type_code="CC"
        )
        cls.prize_type = PrizeType.objects.create(
            prize_type_name="Dinero",
            prize_type_code="DIN",
            prize_type_description="Premio en efectivo"
        )
        
        # === ESTADOS DE RIFA ===
        cls.state_active = StateRaffle.objects.create(
            state_raffle_name="Activo",
            state_raffle_code="ACT",
            state_raffle_description="Rifa activa"
        )
        cls.state_cancelled = StateRaffle.objects.create(
            state_raffle_name="Cancelado",
            state_raffle_code="CAN",
            state_raffle_description="Rifa cancelada"
        )
        cls.state_sorted = StateRaffle.objects.create(
            state_raffle_name="Sorteado",
            state_raffle_code="SOR",
            state_raffle_description="Rifa sorteada"
        )
        
        # === TIPO DE MÉTODO DE PAGO ===
        cls.payment_method_type = PaymentMethodType.objects.create(
            payment_method_type_name="Tarjeta de Crédito",
            payment_method_type_code="CC",
            payment_method_type_description="Pago con tarjeta de crédito",
            payment_method_type_is_active=True
        )
        
        # === USUARIOS ===
        cls.organizer = User.objects.create_user(
            email="organizer@test.com",
            password="testpass123",
            first_name="Organizer",
            last_name="Test",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="11111111",
            city=cls.city
        )
        
        cls.participant1 = User.objects.create_user(
            email="participant1@test.com",
            password="testpass123",
            first_name="Participant",
            last_name="One",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="22222222",
            city=cls.city
        )
        
        cls.participant2 = User.objects.create_user(
            email="participant2@test.com",
            password="testpass123",
            first_name="Participant",
            last_name="Two",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="33333333",
            city=cls.city
        )
        
        # === MÉTODOS DE PAGO ===
        cls.payment_method1 = PaymentMethod.objects.create(
            user=cls.participant1,
            payment_method_type=cls.payment_method_type,
            payment_method_balance=Decimal('1000.00'),
            paymenth_method_holder_name="Participant One",
            paymenth_method_expiration_date=timezone.now().date() + timedelta(days=365)
        )
        cls.payment_method1.set_card_number('1234567890123456')
        cls.payment_method1.save()
        
        cls.payment_method2 = PaymentMethod.objects.create(
            user=cls.participant2,
            payment_method_type=cls.payment_method_type,
            payment_method_balance=Decimal('500.00'),
            paymenth_method_holder_name="Participant Two",
            paymenth_method_expiration_date=timezone.now().date() + timedelta(days=365)
        )
        cls.payment_method2.set_card_number('9876543210987654')
        cls.payment_method2.save()
        
        # === MÉTODO DE PAGO ORGANIZADOR ===
        cls.organizer_payment_method = PaymentMethod.objects.create(
            user=cls.organizer,
            payment_method_type=cls.payment_method_type,
            payment_method_balance=Decimal('10000.00'),
            paymenth_method_holder_name="Organizer Test",
            paymenth_method_expiration_date=timezone.now().date() + timedelta(days=365)
        )
        cls.organizer_payment_method.set_card_number('5555666677778888')
        cls.organizer_payment_method.save()
        
        # === RIFA PRINCIPAL ===
        cls.main_raffle = Raffle.objects.create(
            raffle_name="Rifa Principal Test",
            raffle_description="Rifa para testing optimizado",
            raffle_start_date=timezone.now() - timedelta(days=1),
            raffle_draw_date=timezone.now() + timedelta(days=7),
            raffle_minimum_numbers_sold=2,
            raffle_number_amount=20,
            raffle_number_price=Decimal('10.00'),
            raffle_prize_amount=Decimal('180.00'),
            raffle_prize_type=cls.prize_type,
            raffle_state=cls.state_active,
            raffle_created_by=cls.organizer,
            raffle_creator_payment_method=cls.organizer_payment_method
        )

        # === USUARIO ADMINISTRADOR ===
        cls.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="adminpass",
            first_name="Admin",
            last_name="Cuenta",
            gender=cls.gender,
            document_type=cls.document_type,
            document_number="0000000000",
            city=cls.city
        )
        cls.admin_payment_method = PaymentMethod.objects.create(
            user=cls.admin_user,
            payment_method_type=cls.payment_method_type,
            payment_method_balance=Decimal('0.00'),
            paymenth_method_holder_name="Admin Cuenta",
            paymenth_method_expiration_date=timezone.now().date() + timedelta(days=365)
        )
        cls.admin_payment_method.set_card_number('0000111122223333')
        cls.admin_payment_method.save()

    def setUp(self):
        """Configuración antes de cada test"""
        # Limpiar tickets de tests anteriores
        Ticket.objects.filter(raffle=self.main_raffle).delete()
        
        # Restaurar saldos originales
        self.payment_method1.payment_method_balance = Decimal('1000.00')
        self.payment_method1.save()
        self.payment_method2.payment_method_balance = Decimal('500.00')
        self.payment_method2.save()
        # Inicializar saldo admin para pruebas de sorteo y reembolso
        self.admin_payment_method.payment_method_balance = Decimal('0.00')
        self.admin_payment_method.save()
    # ==================== TESTS CRÍTICOS DE COMPRA ====================
    
    def test_ticket_purchase_success(self):
        """TEST CRÍTICO: Compra exitosa de ticket"""
        ticket = Ticket.purchase_ticket(
            user=self.participant1,
            raffle=self.main_raffle,
            number=1,
            payment_method=self.payment_method1
        )
        
        # Verificaciones esenciales
        self.assertEqual(ticket.user, self.participant1)
        self.assertEqual(ticket.raffle, self.main_raffle)
        self.assertEqual(ticket.number, 1)
        self.assertFalse(ticket.is_winner)
        self.assertEqual(ticket.payment_method, self.payment_method1)
        
        # Verificar descuento
        self.payment_method1.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('990.00'))
        self.admin_payment_method.refresh_from_db()
        self.assertEqual(self.admin_payment_method.payment_method_balance, Decimal('10.00'))

    def test_ticket_purchase_insufficient_balance(self):
        """TEST CRÍTICO: Error por saldo insuficiente"""
        # Reducir saldo
        self.payment_method1.payment_method_balance = Decimal('5.00')
        self.payment_method1.save()
        
        with self.assertRaises(ValidationError) as context:
            Ticket.purchase_ticket(
                user=self.participant1,
                raffle=self.main_raffle,
                number=1,
                payment_method=self.payment_method1
            )
        
        self.assertIn('Saldo insuficiente', str(context.exception))

    def test_ticket_purchase_duplicate_number(self):
        """TEST CRÍTICO: Error al comprar número ya vendido"""
        # Comprar número 1
        Ticket.purchase_ticket(
            user=self.participant1,
            raffle=self.main_raffle,
            number=1,
            payment_method=self.payment_method1
        )
        
        # Intentar comprar mismo número
        with self.assertRaises(ValidationError) as context:
            Ticket.purchase_ticket(
                user=self.participant2,
                raffle=self.main_raffle,
                number=1,
                payment_method=self.payment_method2
            )
        
        self.assertIn('no está disponible', str(context.exception))

    def test_payment_method_ownership_validation(self):
        """TEST CRÍTICO: Validación de propiedad del método de pago"""
        with self.assertRaises(ValidationError) as context:
            Ticket.purchase_ticket(
                user=self.participant1,
                raffle=self.main_raffle,
                number=1,
                payment_method=self.payment_method2  # Método del participant2
            )
        
        self.assertIn('no pertenece al usuario', str(context.exception))

    # ==================== TESTS CRÍTICOS DE REEMBOLSO ====================
    
    def test_ticket_refund_success(self):
        """TEST CRÍTICO: Reembolso exitoso de ticket"""
        # Comprar ticket
        ticket = Ticket.purchase_ticket(
            user=self.participant1,
            raffle=self.main_raffle,
            number=1,
            payment_method=self.payment_method1
        )
        
        # Verificar descuento
        self.payment_method1.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('990.00'))
        
        # Reembolsar
        ticket.refund_ticket()
        
        # Verificar reembolso
        self.payment_method1.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('1000.00'))
        
        # Verificar eliminación
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())

    def test_winner_ticket_refund_allowed(self):
        """TEST CRÍTICO: Reembolso de ticket ganador permitido (casos administrativos)"""
        # Comprar y marcar como ganador
        ticket = Ticket.purchase_ticket(
            user=self.participant1,
            raffle=self.main_raffle,
            number=1,
            payment_method=self.payment_method1
        )
        ticket.is_winner = True
        ticket.save()
        
        # Verificar descuento inicial
        self.payment_method1.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('990.00'))
        
        # Reembolsar (debe funcionar para casos administrativos)
        ticket.refund_ticket()
        
        # Verificar reembolso
        self.payment_method1.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('1000.00'))

    # ==================== TESTS CRÍTICOS DE PROPIEDADES DE RIFA ====================
    
    def test_raffle_available_numbers(self):
        """TEST CRÍTICO: Números disponibles de la rifa"""
        # Estado inicial
        available = self.main_raffle.available_numbers
        self.assertEqual(len(available), 20)
        self.assertEqual(available[0], 1)
        self.assertEqual(available[-1], 20)
        
        # Comprar algunos números
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 10, self.payment_method1)
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 20, self.payment_method1)
        
        # Verificar disponibilidad
        available = self.main_raffle.available_numbers
        self.assertEqual(len(available), 17)  # 20 - 3 = 17
        self.assertNotIn(1, available)
        self.assertNotIn(10, available)
        self.assertNotIn(20, available)
        self.assertIn(2, available)
        self.assertIn(15, available)

    def test_raffle_sales_properties(self):
        """TEST CRÍTICO: Propiedades de ventas de la rifa"""
        # Estado inicial
        self.assertEqual(self.main_raffle.numbers_sold, 0)
        self.assertEqual(self.main_raffle.numbers_available, 20)
        self.assertFalse(self.main_raffle.minimum_reached)
        
        # Después de compras
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)
        
        self.assertEqual(self.main_raffle.numbers_sold, 2)
        self.assertEqual(self.main_raffle.numbers_available, 18)
        self.assertTrue(self.main_raffle.minimum_reached)
        
        # Verificar números vendidos
        sold_numbers = self.main_raffle.sold_numbers
        self.assertIn(1, sold_numbers)
        self.assertIn(2, sold_numbers)

    def test_raffle_status_display(self):
        """TEST CRÍTICO: Display de estado de la rifa"""
        # Estado inicial: ventas activas sin mínimo
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        status_display = self.main_raffle.status_display
        self.assertIn("faltan 1 para alcanzar mínimo", status_display)
        
        # Alcanzar mínimo
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)
        status_display = self.main_raffle.status_display
        self.assertIn("mínimo alcanzado", status_display)

    # ==================== TESTS CRÍTICOS DE SORTEO ====================
    
    def test_raffle_draw_validation(self):
        """TEST CRÍTICO: Validaciones para sorteo"""
        # Con fecha futura, sin tickets
        can_draw, message = self.main_raffle.can_execute_draw()
        self.assertFalse(can_draw)
        self.assertIn("No se alcanzó el mínimo", message)

        # Comprar tickets primero (mientras la rifa está activa)
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)

        # Ahora cambiar fecha al pasado - debe poder sortear
        past_date = timezone.now() - timedelta(minutes=1)
        Raffle.objects.filter(id=self.main_raffle.id).update(raffle_draw_date=past_date)
        self.main_raffle.refresh_from_db()

        can_draw, message = self.main_raffle.can_execute_draw()
        self.assertTrue(can_draw)
        self.assertEqual(message, "Listo para sortear")

    def test_raffle_draw_success(self):
        """TEST CRÍTICO: Sorteo exitoso"""
        # Inicializar saldo de la cuenta conjunta (admin) para cubrir el premio
        initial_admin_balance = Decimal('200.00')
        self.admin_payment_method.payment_method_balance = initial_admin_balance
        self.admin_payment_method.save()

        # Comprar tickets para alcanzar mínimo (2 tickets × 10.00 = 20.00)
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)

        # Ajustar fecha para permitir sorteo (usando update para evitar validaciones)
        past_date = timezone.now() - timedelta(minutes=1)
        Raffle.objects.filter(id=self.main_raffle.id).update(raffle_draw_date=past_date)
        self.main_raffle.refresh_from_db()

        # Verificar que está listo
        can_draw, message = self.main_raffle.can_execute_draw()
        self.assertTrue(can_draw)
        # Antes del sorteo: cuenta conjunta debe tener balance inicial + dinero de tickets vendidos
        # 200.00 + 20.00 = 220.00
        self.admin_payment_method.refresh_from_db()
        self.assertEqual(self.admin_payment_method.payment_method_balance, Decimal('220.00'))

        # Guardar balance inicial del organizador (debe cubrir el déficit)
        # Déficit = 180.00 (premio) - 20.00 (ingresos) = 160.00
        initial_organizer_balance = Decimal('10000.00')
        self.organizer_payment_method.payment_method_balance = initial_organizer_balance
        self.organizer_payment_method.save()

        # Ejecutar sorteo
        result = self.main_raffle.execute_raffle_draw()

        # Verificaciones críticas
        self.assertIn('message', result)
        self.assertIn('winner_user', result)
        self.assertIn('winner_number', result)
        self.assertEqual(result['tickets_sold'], 2)
        
        # Después del sorteo: 
        # Ingresos: 20.00
        # Premio: 180.00
        # Déficit: 160.00
        # 
        # Flujo:
        # 1. Organizador paga déficit: 10000.00 - 160.00 = 9840.00
        # 2. Cuenta conjunta recibe déficit: 220.00 + 160.00 = 380.00
        # 3. Cuenta conjunta paga premio: 380.00 - 180.00 = 200.00
        
        self.admin_payment_method.refresh_from_db()
        self.assertEqual(self.admin_payment_method.payment_method_balance, Decimal('200.00'))
        
        self.organizer_payment_method.refresh_from_db()
        self.assertEqual(self.organizer_payment_method.payment_method_balance, Decimal('9840.00'))
        
        # Verificar ganador asignado
        self.main_raffle.refresh_from_db()
        self.assertIsNotNone(self.main_raffle.raffle_winner)

        # Verificar ticket ganador
        winning_tickets = Ticket.objects.filter(raffle=self.main_raffle, is_winner=True)
        self.assertEqual(winning_tickets.count(), 1)

    def test_cannot_draw_twice(self):
        """TEST CRÍTICO: No se puede sortear dos veces"""
        # Inicializar saldo admin para cubrir el premio
        self.admin_payment_method.payment_method_balance = Decimal('200.00')
        self.admin_payment_method.save()

        # Inicializar saldo del organizador para cubrir déficit
        self.organizer_payment_method.payment_method_balance = Decimal('10000.00')
        self.organizer_payment_method.save()

        # Preparar sorteo
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)

        past_date = timezone.now() - timedelta(minutes=1)
        Raffle.objects.filter(id=self.main_raffle.id).update(raffle_draw_date=past_date)
        self.main_raffle.refresh_from_db()

        # Primer sorteo
        self.main_raffle.execute_raffle_draw()

        # Intentar segundo sorteo
        can_draw, message = self.main_raffle.can_execute_draw()
        self.assertFalse(can_draw)
        self.assertIn('ya fue ejecutado', message)

    def test_organizer_insufficient_balance_for_deficit(self):
        """TEST CRÍTICO: Sorteo cancela y reembolsa si organizador no puede cubrir déficit"""
        # Inicializar saldo admin
        self.admin_payment_method.payment_method_balance = Decimal('200.00')
        self.admin_payment_method.save()

        # Organizador con saldo insuficiente (necesita 160 para cubrir déficit)
        self.organizer_payment_method.payment_method_balance = Decimal('100.00')
        self.organizer_payment_method.save()

        # Guardar saldos iniciales de participantes
        initial_participant1_balance = self.payment_method1.payment_method_balance
        initial_participant2_balance = self.payment_method2.payment_method_balance

        # Comprar tickets (20.00 de ingresos, 180.00 de premio = -160.00 déficit)
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)

        # Verificar que se descontó el dinero
        self.payment_method1.refresh_from_db()
        self.payment_method2.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, initial_participant1_balance - Decimal('10.00'))
        self.assertEqual(self.payment_method2.payment_method_balance, initial_participant2_balance - Decimal('10.00'))

        # Ajustar fecha para permitir sorteo
        past_date = timezone.now() - timedelta(minutes=1)
        Raffle.objects.filter(id=self.main_raffle.id).update(raffle_draw_date=past_date)
        self.main_raffle.refresh_from_db()

        # Intentar sortear debe fallar, cancelar y reembolsar
        with self.assertRaises(ValueError) as context:
            self.main_raffle.execute_raffle_draw()
        
        self.assertIn('Sorteo cancelado', str(context.exception))
        self.assertIn('no tiene saldo suficiente para cubrir el déficit', str(context.exception))
        self.assertIn('160.00', str(context.exception))
        self.assertIn('Se han reembolsado todos los tickets', str(context.exception))

        # Verificar que la rifa fue cancelada
        self.main_raffle.refresh_from_db()
        from raffleInfo.models import StateRaffle
        cancelled_state = StateRaffle.objects.filter(state_raffle_code__iexact='CAN').first()
        self.assertEqual(self.main_raffle.raffle_state, cancelled_state)

        # Verificar que se reembolsaron los tickets
        self.assertEqual(Ticket.objects.filter(raffle=self.main_raffle).count(), 0)

        # Verificar que se devolvió el dinero a los participantes
        self.payment_method1.refresh_from_db()
        self.payment_method2.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, initial_participant1_balance)
        self.assertEqual(self.payment_method2.payment_method_balance, initial_participant2_balance)

    # ==================== TESTS CRÍTICOS DE CANCELACIÓN ====================
    
    def test_organizer_soft_delete_success(self):
        """TEST CRÍTICO: Cancelación exitosa por organizador"""
        # Comprar tickets
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)
        
        # Verificar descuentos
        self.payment_method1.refresh_from_db()
        self.payment_method2.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('990.00'))
        self.assertEqual(self.payment_method2.payment_method_balance, Decimal('490.00'))
        
        # Cancelar rifa
        result = self.main_raffle.soft_delete_and_refund(self.organizer)
        
        # Verificaciones críticas
        self.assertEqual(result['tickets_refunded'], 2)
        self.assertEqual(result['total_amount_refunded'], Decimal('20.00'))
        self.assertEqual(result['cancellation_type'], 'organizer_soft_delete')
        
        # Verificar reembolsos
        self.payment_method1.refresh_from_db()
        self.payment_method2.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('1000.00'))
        self.assertEqual(self.payment_method2.payment_method_balance, Decimal('500.00'))
        
        # Verificar eliminación de tickets
        self.assertFalse(Ticket.objects.filter(raffle=self.main_raffle).exists())

    def test_only_organizer_can_cancel(self):
        """TEST CRÍTICO: Solo organizador puede cancelar"""
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        
        with self.assertRaises(ValidationError) as context:
            self.main_raffle.soft_delete_and_refund(self.participant1)  # No es organizador
        
        self.assertIn('Solo el organizador puede cancelar', str(context.exception))

    def test_admin_cancel_with_refunds(self):
        """TEST CRÍTICO: Cancelación administrativa con reembolsos"""
        # Comprar tickets
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)
        
        # Cancelación administrativa
        admin_reason = "Irregularidades detectadas en la rifa"
        result = self.main_raffle.cancel_raffle_and_refund(admin_reason)
        
        # Verificaciones críticas
        self.assertEqual(result['admin_reason'], admin_reason)
        self.assertEqual(result['tickets_refunded'], 2)
        self.assertFalse(result['was_previously_drawn'])
        self.assertEqual(result['total_amount_refunded'], Decimal('20.00'))
        
        # Verificar reembolsos
        self.payment_method1.refresh_from_db()
        self.payment_method2.refresh_from_db()
        self.assertEqual(self.payment_method1.payment_method_balance, Decimal('1000.00'))
        self.assertEqual(self.payment_method2.payment_method_balance, Decimal('500.00'))

    # ==================== TESTS CRÍTICOS DE VALIDACIONES ====================
    
    def test_ticket_number_range_validation(self):
        """TEST CRÍTICO: Validación de rango de números"""
        # Número fuera de rango
        ticket = Ticket(
            user=self.participant1,
            raffle=self.main_raffle,
            number=25,  # Fuera del rango 1-20
            payment_method=self.payment_method1
        )
        
        with self.assertRaises(ValidationError) as context:
            ticket.clean()
        
        self.assertIn('debe estar entre 1 y 20', str(context.exception))

    def test_ticket_str_representation(self):
        """TEST CRÍTICO: Representación en string del ticket"""
        ticket = Ticket.purchase_ticket(
            user=self.participant1,
            raffle=self.main_raffle,
            number=7,
            payment_method=self.payment_method1
        )
        
        ticket_str = str(ticket)
        self.assertIn('#007', ticket_str)  # Número formateado
        self.assertIn('Rifa Principal Test', ticket_str)
        self.assertIn('participant1@test.com', ticket_str)
        self.assertIn('Tarjeta de Crédito', ticket_str)

    def test_payment_method_card_security(self):
        """TEST CRÍTICO: Seguridad del número de tarjeta"""
        original_number = '1234567890123456'
        
        # Verificar que no se almacena en texto plano
        self.assertNotEqual(
            self.payment_method1.paymenth_method_card_number_hash, 
            original_number
        )
        
        # Verificar funciones de seguridad
        self.assertTrue(self.payment_method1.check_card_number(original_number))
        self.assertFalse(self.payment_method1.check_card_number('9999999999999999'))
        self.assertEqual(self.payment_method1.last_digits, '3456')
        self.assertEqual(
            self.payment_method1.get_masked_card_number(), 
            '**** **** **** 3456'
        )

    def test_raffle_revenue_calculation(self):
        """TEST CRÍTICO: Cálculo de revenue de la rifa (solo ventas)"""
        # Estado inicial
        self.assertEqual(self.main_raffle.total_revenue, Decimal('0.00'))

        # Después de vender tickets
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        self.assertEqual(self.main_raffle.total_revenue, Decimal('10.00'))

        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)
        self.assertEqual(self.main_raffle.total_revenue, Decimal('20.00'))

        # Comprar más tickets
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 3, self.payment_method1)
        self.assertEqual(self.main_raffle.total_revenue, Decimal('30.00'))

    def test_admin_balance_after_raffle_draw(self):
        """TEST: Verifica el saldo de la cuenta conjunta después del sorteo"""
        # Inicializar saldo de la cuenta conjunta (admin) para poder comprar tickets y pagar premio
        initial_admin_balance = Decimal('200.00')
        self.admin_payment_method.payment_method_balance = initial_admin_balance
        self.admin_payment_method.save()

        # Comprar tickets (3 tickets × 10.00 = 30.00 que van a la cuenta conjunta)
        Ticket.purchase_ticket(self.participant1, self.main_raffle, 1, self.payment_method1)
        Ticket.purchase_ticket(self.participant2, self.main_raffle, 2, self.payment_method2)
        Ticket.purchase_ticket(self.admin_user, self.main_raffle, 3, self.admin_payment_method)

        # Después de las compras, la cuenta conjunta debe tener:
        # - 200 (inicial)
        # - +10 de participant1
        # - +10 de participant2  
        # - +10 de admin (se descuenta 10 y se agrega 10, neto = 0 pero se ejecutan ambas operaciones)
        # Total: 200 + 10 + 10 + 10 = 230.00
        self.admin_payment_method.refresh_from_db()
        self.assertEqual(self.admin_payment_method.payment_method_balance, Decimal('230.00'))

        # Ajustar fecha para permitir sorteo
        from django.utils import timezone
        from datetime import timedelta
        past_date = timezone.now() - timedelta(minutes=1)
        from raffle.models import Raffle
        Raffle.objects.filter(id=self.main_raffle.id).update(raffle_draw_date=past_date)
        self.main_raffle.refresh_from_db()

        # Ejecutar sorteo
        result = self.main_raffle.execute_raffle_draw()

        # Verificar saldo de la cuenta conjunta después del sorteo
        # Ingresos: 30.00
        # Premio: 180.00
        # Déficit: 150.00
        # 
        # Flujo:
        # 1. Organizador paga déficit: 10000.00 - 150.00 = 9850.00
        # 2. Cuenta conjunta recibe déficit: 230.00 + 150.00 = 380.00
        # 3. Cuenta conjunta paga premio: 380.00 - 180.00 = 200.00
        self.admin_payment_method.refresh_from_db()
        self.assertEqual(self.admin_payment_method.payment_method_balance, Decimal('200.00'))
        
        # Verificar que el organizador pagó el déficit
        self.organizer_payment_method.refresh_from_db()
        self.assertEqual(self.organizer_payment_method.payment_method_balance, Decimal('9850.00'))

        # Verificaciones adicionales
        self.assertIn('message', result)
        self.assertIn('winner_user', result)
        self.assertIn('winner_number', result)
        self.assertEqual(result['tickets_sold'], 3)

        # Verificar ganador asignado
        self.main_raffle.refresh_from_db()
        self.assertIsNotNone(self.main_raffle.raffle_winner)

        # Verificar ticket ganador
        winning_tickets = Ticket.objects.filter(raffle=self.main_raffle, is_winner=True)
        self.assertEqual(winning_tickets.count(), 1)