"""
Tests para el sistema automático de sorteo de rifas.
Cubre signals, comando de gestión y procesamiento automático.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from location.models import City, Country, State
from raffle.models import Raffle
from raffleInfo.models import PrizeType, StateRaffle
from tickets.models import Ticket
from user.models import User
from userInfo.models import DocumentType, Gender, PaymentMethod, PaymentMethodType


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
            gender_name="Male", defaults={"gender_code": "M"}
        )
        self.document_type, _ = DocumentType.objects.get_or_create(
            document_type_name="Cedula", defaults={"document_type_code": "CC"}
        )

        # Ubicación
        self.country, _ = Country.objects.get_or_create(
            country_name="Colombia", defaults={"country_code": "CO"}
        )
        self.state, _ = State.objects.get_or_create(
            state_name="Bogotá",
            defaults={"state_code": "BOG", "state_country": self.country},
        )
        self.city, _ = City.objects.get_or_create(
            city_name="Bogotá", defaults={"city_code": "BOG", "city_state": self.state}
        )

        # Usuarios
        self.user = User.objects.create_user(
            email="user@test.com",
            password="pass123",
            first_name="Test",
            last_name="User",
            gender=self.gender,
            document_type=self.document_type,
            document_number="12345678",
            city=self.city,
        )

        self.participant1 = User.objects.create_user(
            email="participant1@test.com",
            password="pass123",
            first_name="Participant",
            last_name="One",
            gender=self.gender,
            document_type=self.document_type,
            document_number="87654321",
            city=self.city,
        )

        self.participant2 = User.objects.create_user(
            email="participant2@test.com",
            password="pass123",
            first_name="Participant",
            last_name="Two",
            gender=self.gender,
            document_type=self.document_type,
            document_number="11111111",
            city=self.city,
        )

        # Datos para rifas
        self.prize_type, _ = PrizeType.objects.get_or_create(
            prize_type_name="Dinero", defaults={"prize_type_code": "DIN"}
        )
        self.active_state, _ = StateRaffle.objects.get_or_create(
            state_raffle_name="Activa", defaults={"state_raffle_code": "ACT"}
        )
        self.cancelled_state, _ = StateRaffle.objects.get_or_create(
            state_raffle_name="Cancelada", defaults={"state_raffle_code": "CAN"}
        )
        self.sorted_state, _ = StateRaffle.objects.get_or_create(
            state_raffle_name="Sorteada", defaults={"state_raffle_code": "SOR"}
        )  # Método de pago para tickets
        self.payment_method_type, _ = PaymentMethodType.objects.get_or_create(
            payment_method_type_name="Efectivo",
            defaults={"payment_method_type_code": "EFE"},
        )
        from datetime import date

        self.payment_method = PaymentMethod.objects.create(
            user=self.participant1,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Participant One",
            paymenth_method_card_number_hash="hashed_card_123",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="1234",
            payment_method_balance=Decimal("1000.00"),
        )
        self.payment_method2 = PaymentMethod.objects.create(
            user=self.participant2,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Participant Two",
            paymenth_method_card_number_hash="hashed_card_456",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="5678",
            payment_method_balance=Decimal("1000.00"),
        )

        # Método de pago para el organizador (self.user)
        self.organizer_payment_method = PaymentMethod.objects.create(
            user=self.user,
            payment_method_type=self.payment_method_type,
            paymenth_method_holder_name="Test User",
            paymenth_method_card_number_hash="hashed_card_organizer",
            paymenth_method_expiration_date=date(2026, 12, 31),
            last_digits="9999",
            payment_method_balance=Decimal("10000.00"),
        )

        # Usuario admin y método de pago admin para cancelaciones automáticas
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="adminpass",
            first_name="Admin",
            last_name="Cuenta",
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
            payment_method_balance=Decimal("0.00"),
        )

    def create_expired_raffle(self, minimum_sold=3, numbers_amount=10, days_expired=1):
        """Helper para crear rifas vencidas"""
        past_date = timezone.now() - timedelta(days=days_expired)
        start_date = past_date - timedelta(
            days=2
        )  # Fecha inicio anterior a fecha sorteo

        raffle = Raffle.objects.create(
            raffle_name="Rifa Test Vencida",
            raffle_description="Test rifa vencida",
            raffle_start_date=start_date,
            raffle_draw_date=past_date,
            raffle_minimum_numbers_sold=minimum_sold,
            raffle_number_amount=numbers_amount,
            raffle_number_price=Decimal("10.00"),
            raffle_prize_amount=Decimal("100.00"),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method,
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
            raffle_name="Rifa Test Con Mínimo",
            raffle_start_date=start_date,
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=2,
            raffle_number_amount=5,
            raffle_number_price=Decimal("10.00"),
            raffle_prize_amount=Decimal("100.00"),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method,
        )

        # Vender tickets para alcanzar el mínimo
        Ticket.objects.create(
            user=self.participant1,
            raffle=raffle,
            number=1,
            payment_method=self.payment_method,
        )
        Ticket.objects.create(
            user=self.participant2,
            raffle=raffle,
            number=2,
            payment_method=self.payment_method2,
        )

        # Ahora vencer la rifa manualmente usando update (bypass validation)
        past_date = timezone.now() - timedelta(hours=2)
        start_date = past_date - timedelta(hours=1)  # Asegurar fecha inicio anterior
        Raffle.objects.filter(id=raffle.id).update(
            raffle_draw_date=past_date, raffle_start_date=start_date
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
            raffle_name="Rifa Futura",
            raffle_draw_date=future_date,
            raffle_minimum_numbers_sold=3,
            raffle_number_amount=10,
            raffle_number_price=Decimal("10.00"),
            raffle_prize_amount=Decimal("100.00"),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method,
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
            raffle_name="Rifa Recién Vencida",
            raffle_start_date=start_date,
            raffle_draw_date=recent_past,
            raffle_minimum_numbers_sold=3,
            raffle_number_amount=10,
            raffle_number_price=Decimal("10.00"),
            raffle_prize_amount=Decimal("100.00"),
            raffle_prize_type=self.prize_type,
            raffle_state=self.active_state,
            raffle_created_by=self.user,
            raffle_creator_payment_method=self.organizer_payment_method,
        )

        # Simular carga desde BD
        with transaction.atomic():
            loaded_raffle = Raffle.objects.get(id=raffle.id)

        # Verificar que NO se procesó (muy reciente)
        loaded_raffle.refresh_from_db()
        self.assertEqual(loaded_raffle.raffle_state, self.active_state)
