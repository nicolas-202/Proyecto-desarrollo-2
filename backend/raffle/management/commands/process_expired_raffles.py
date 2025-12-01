from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from raffle.models import Raffle
from raffleInfo.models import StateRaffle
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Procesar rifas vencidas: sortear las que alcanzaron el mínimo, cancelar las que no'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se haría sin ejecutar los cambios',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Procesar incluso rifas vencidas recientemente',
        )
    
    def handle(self, *args, **options):
        now = timezone.now()
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write("=" * 60)
        self.stdout.write(f"🎯 PROCESANDO RIFAS VENCIDAS")
        self.stdout.write(f"Fecha actual: {now}")
        self.stdout.write(f"Modo: {'DRY RUN' if dry_run else 'EJECUCIÓN REAL'}")
        self.stdout.write("=" * 60)
        
        # Buscar rifas que pasaron su fecha de sorteo
        expired_raffles = Raffle.objects.filter(
            raffle_draw_date__lt=now,
            raffle_winner__isnull=True
        ).select_related('raffle_state', 'raffle_created_by')
        
        if not force:
            # Solo procesar rifas vencidas hace más de 1 hora
            one_hour_ago = now - timezone.timedelta(hours=1)
            expired_raffles = expired_raffles.filter(raffle_draw_date__lt=one_hour_ago)
        
        total_rifas = expired_raffles.count()
        self.stdout.write(f"\n📊 Rifas vencidas encontradas: {total_rifas}")
        
        if total_rifas == 0:
            self.stdout.write(self.style.SUCCESS("✅ No hay rifas vencidas para procesar"))
            return
        
        # Buscar estado cancelado
        cancelled_state = StateRaffle.objects.filter(
            state_raffle_code__iexact='CAN'
        ).first() or StateRaffle.objects.filter(
            state_raffle_name__icontains='cancel'
        ).first()
        
        if not cancelled_state:
            raise CommandError("❌ No se encontró estado 'Cancelado' en la base de datos")
        
        stats = {
            'sorteadas': 0,
            'canceladas': 0,
            'errores': 0,
            'total_reembolsado': 0,
            'tickets_reembolsados': 0
        }
        
        for i, raffle in enumerate(expired_raffles, 1):
            self.stdout.write(f"\n--- Procesando rifa {i}/{total_rifas} ---")
            self.stdout.write(f"ID: {raffle.id}")
            self.stdout.write(f"Nombre: {raffle.raffle_name}")
            self.stdout.write(f"Fecha sorteo: {raffle.raffle_draw_date}")
            self.stdout.write(f"Días de retraso: {(now - raffle.raffle_draw_date).days}")
            self.stdout.write(f"Números vendidos: {raffle.numbers_sold}/{raffle.raffle_minimum_numbers_sold}")
            self.stdout.write(f"Estado actual: {raffle.raffle_state.state_raffle_name}")
            
            try:
                if raffle.minimum_reached:
                    # Sortear automáticamente
                    self.stdout.write(f"🎲 Mínimo alcanzado -> SORTEAR")
                    
                    if not dry_run:
                        result = raffle.execute_raffle_draw()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ SORTEADA - Ganador: {result.get('winner_user', 'N/A')} "
                                f"(Número: {result.get('winner_number', 'N/A')})"
                            )
                        )
                        stats['sorteadas'] += 1
                    else:
                        self.stdout.write(self.style.WARNING("🔄 Se sortearía"))
                        
                else:
                    # Cancelar automáticamente CON REEMBOLSOS
                    self.stdout.write(f"❌ Mínimo NO alcanzado -> CANCELAR CON REEMBOLSOS")
                    
                    if not dry_run:
                        result = raffle.cancel_raffle_and_refund(
                            admin_reason="Cancelación automática por comando: mínimo no alcanzado"
                        )
                        self.stdout.write(
                            self.style.WARNING(
                                f"📋 CANCELADA CON REEMBOLSOS - "
                                f"Tickets: {result['tickets_refunded']}, "
                                f"Monto: ${result['total_amount_refunded']}"
                            )
                        )
                        stats['canceladas'] += 1
                        stats['tickets_reembolsados'] += result['tickets_refunded']
                        stats['total_reembolsado'] += result['total_amount_refunded']
                    else:
                        self.stdout.write(self.style.WARNING("🔄 Se cancelaría CON REEMBOLSOS"))
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ ERROR procesando rifa {raffle.id}: {e}")
                )
                stats['errores'] += 1
        
        # Resumen final
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📋 RESUMEN DE PROCESAMIENTO")
        self.stdout.write("=" * 60)
        
        if not dry_run:
            self.stdout.write(f"🎲 Rifas sorteadas: {stats['sorteadas']}")
            self.stdout.write(f"❌ Rifas canceladas: {stats['canceladas']}")
            if stats['canceladas'] > 0:
                self.stdout.write(f"💰 Tickets reembolsados: {stats['tickets_reembolsados']}")
                self.stdout.write(f"💵 Total reembolsado: ${stats['total_reembolsado']}")
            self.stdout.write(f"⚠️  Errores encontrados: {stats['errores']}")
            
            if stats['errores'] == 0:
                self.stdout.write(self.style.SUCCESS("\n✅ Procesamiento completado exitosamente"))
            else:
                self.stdout.write(self.style.WARNING(f"\n⚠️  Procesamiento completado con {stats['errores']} errores"))
        else:
            self.stdout.write(self.style.WARNING("🔄 Ejecutar sin --dry-run para aplicar los cambios"))
        
        self.stdout.write("=" * 60)