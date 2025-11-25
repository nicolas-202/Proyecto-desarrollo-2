from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password
from location.models import Country, State, City
from userInfo.models import DocumentType, Gender, PaymentMethodType
from raffleInfo.models import PrizeType, StateRaffle
from user.models import User
import os


class Command(BaseCommand):
    help = 'Inicializa la base de datos con datos esenciales para el sistema de rifas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la recreación de datos (elimina datos existentes)',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            self.clear_existing_data()

        with transaction.atomic():
            self.create_locations()
            self.create_document_types()
            self.create_genders()
            self.create_payment_method_types()
            self.create_prize_types()
            self.create_raffle_states()
            self.create_admin_user()
            self.create_admin_user_payment_method()  # NUEVO: Crear método de pago admin
            self.create_user_1()  # NUEVO: Crear usuario regular
            self.create_user1_payment_method()  # NUEVO: Crear método de pago usuario 1

        self.stdout.write(
            self.style.SUCCESS('✅ Datos base inicializados correctamente')
        )

    def clear_existing_data(self):
        """Elimina datos existentes en orden para evitar violaciones de FK"""
        # Eliminar en orden inverso a las dependencias
        User.objects.all().delete()
        City.objects.all().delete()
        State.objects.all().delete()
        Country.objects.all().delete()
        DocumentType.objects.all().delete()
        Gender.objects.all().delete()
        PaymentMethodType.objects.all().delete()
        PrizeType.objects.all().delete()
        StateRaffle.objects.all().delete()

    def create_locations(self):
        """Crear ubicaciones base de Colombia"""
        self.stdout.write('Creando ubicaciones base...')
        
        # País
        colombia, created = Country.objects.get_or_create(
            country_code='CO',
            defaults={
                'country_name': 'Colombia',
                'country_description': 'República de Colombia',
                'country_is_active': True
            }
        )
        if created:
            self.stdout.write(f'  ✓ País creado: {colombia.country_name}')
        
        # Estados principales
        states_data = [
            ('VAL', 'Valle del Cauca', 'Departamento del Valle del Cauca'),
        ]
        
        states = {}
        for code, name, desc in states_data:
            state, created = State.objects.get_or_create(
                state_code=code,
                state_country=colombia,
                defaults={
                    'state_name': name,
                    'state_description': desc,
                    'state_is_active': True
                }
            )
            states[code] = state
            if created:
                self.stdout.write(f'  ✓ Estado creado: {state.state_name}')
        
        # Ciudades principales
        cities_data = [
            ('CAL', 'VAL', 'Cali', 'Capital del Valle del Cauca'),
        ]
        
        for city_code, state_code, city_name, desc in cities_data:
            city, created = City.objects.get_or_create(
                city_code=city_code,
                city_state=states[state_code],
                defaults={
                    'city_name': city_name,
                    'city_description': desc,
                    'city_is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Ciudad creada: {city.city_name}')

    def create_document_types(self):
        """Crear tipos de documento colombianos"""
        self.stdout.write('Creando tipos de documento...')
        
        document_types = [
            ('CC', 'Cédula de Ciudadanía', 'Documento de identificación para ciudadanos colombianos'),
        ]
        for code, name, desc in document_types:
            doc_type, created = DocumentType.objects.get_or_create(
                document_type_code=code,
                defaults={
                    'document_type_name': name,
                    'document_type_description': desc,
                    'document_type_is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Tipo documento creado: {doc_type.document_type_name}')

    def create_genders(self):
        """Crear géneros"""
        self.stdout.write('Creando géneros...')
        
        genders = [
            ('M', 'Masculino', 'Género masculino'),
            ('F', 'Femenino', 'Género femenino')
        ]
        
        for code, name, desc in genders:
            gender, created = Gender.objects.get_or_create(
                gender_code=code,
                defaults={
                    'gender_name': name,
                    'gender_description': desc,
                    'gender_is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Género creado: {gender.gender_name}')

    def create_payment_method_types(self):
        """Crear tipos de método de pago"""
        self.stdout.write('Creando tipos de método de pago...')
        
        payment_types = [
            ('TDEB', 'Tarjeta Débito', 'Tarjeta débito bancaria')
        ]
        
        for code, name, desc in payment_types:
            payment_type, created = PaymentMethodType.objects.get_or_create(
                payment_method_type_code=code,
                defaults={
                    'payment_method_type_name': name,
                    'payment_method_type_description': desc,
                    'payment_method_type_is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Tipo pago creado: {payment_type.payment_method_type_name}')

    def create_prize_types(self):
        """Crear tipos de premio"""
        self.stdout.write('Creando tipos de premio...')
        
        prize_types = [
            ('DIN', 'Dinero', 'Premio en dinero en efectivo')
        ]
        
        for code, name, desc in prize_types:
            prize_type, created = PrizeType.objects.get_or_create(
                prize_type_code=code,
                defaults={
                    'prize_type_name': name,
                    'prize_type_description': desc,
                    'prize_type_is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Tipo premio creado: {prize_type.prize_type_name}')

    def create_raffle_states(self):
        """Crear estados de rifa"""
        self.stdout.write('Creando estados de rifa...')
        
        raffle_states = [
            ('ACTV', 'Activa', 'Rifa activa y vendiendo números'),
            ('SORT', 'Sorteada', 'Rifa ya sorteada'),
            ('CANC', 'Cancelada', 'Rifa cancelada')
        ]
        
        for code, name, desc in raffle_states:
            state, created = StateRaffle.objects.get_or_create(
                state_raffle_code=code,
                defaults={
                    'state_raffle_name': name,
                    'state_raffle_description': desc,
                    'state_raffle_is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Estado rifa creado: {state.state_raffle_name}')

    def create_admin_user(self):
        """Crear usuario administrador por defecto con cuenta conjunta"""
        self.stdout.write('Creando usuario administrador...')
        
        # Obtener dependencias necesarias
        try:
            colombia = Country.objects.get(country_code='CO')
            valle_state = State.objects.get(state_code='VAL', state_country=colombia)
            cali_city = City.objects.get(city_code='CAL', city_state=valle_state)
            male_gender = Gender.objects.get(gender_code='M')
            cc_document = DocumentType.objects.get(document_type_code='CC')
        except (Country.DoesNotExist, State.DoesNotExist, City.DoesNotExist, 
                Gender.DoesNotExist, DocumentType.DoesNotExist) as e:
            self.stdout.write(
                self.style.ERROR(f'Error: Dependencias no encontradas: {e}')
            )
            return

        # Crear admin solo si no existe
        admin_email = 'admin@rifas.com'
        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_user(
                email=admin_email,
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                gender=male_gender,
                document_type=cc_document,
                document_number='0000000000',  # 10 ceros (cuenta conjunta)
                city=cali_city,
                is_staff=True,
                is_admin=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Usuario admin creado: {admin_user.email}')
            )
            self.stdout.write(
                self.style.WARNING(f'  🔑 Password: admin123 (¡CAMBIAR EN PRODUCCIÓN!)')
            )
        else:
            self.stdout.write(f'  ⚠️  Usuario admin ya existe: {admin_email}')

    def create_admin_user_payment_method(self):
        """Crear método de pago para el usuario administrador (cuenta conjunta)"""
        self.stdout.write('Creando método de pago para el usuario administrador...')
        
        try:
            admin_user = User.objects.get(document_number='0000000000')  # 10 ceros según tu modelo
            debit_card_type = PaymentMethodType.objects.get(payment_method_type_code='TDEB')
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('  ❌ Error: Usuario admin no encontrado (debe tener documento 0000000000)')
            )
            return
        except PaymentMethodType.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('  ❌ Error: Tipo de método de pago TDEB no encontrado')
            )
            return
        
        # Verificar si ya existe
        if admin_user.payment_methods.filter(payment_method_type=debit_card_type).exists():
            self.stdout.write('  ⚠️  Método de pago admin ya existe')
            return
            
        # Importar módulos necesarios
        from datetime import date, timedelta
        from django.contrib.auth.hashers import make_password
        from userInfo.models import PaymentMethod
        
        card_number = '1234567890123456'
        expiration = date.today() + timedelta(days=365*3)
        
        payment_method = PaymentMethod.objects.create(
            user=admin_user,
            payment_method_type=debit_card_type,
            paymenth_method_holder_name='Cuenta Conjunta Sistema',
            paymenth_method_card_number_hash=make_password(card_number),
            paymenth_method_expiration_date=expiration,
            last_digits=card_number[-4:],
            payment_method_balance=10000000.00,  # 10 millones de saldo inicial
            payment_method_is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Método de pago creado para admin - Saldo: ${payment_method.payment_method_balance:,.0f}')
        )

    def create_user_1(self):
        """Crear usuario regular para pruebas"""
        self.stdout.write('Creando usuario regular de prueba...')
        
        # Obtener dependencias necesarias
        try:
            colombia = Country.objects.get(country_code='CO')
            valle_state = State.objects.get(state_code='VAL', state_country=colombia)
            cali_city = City.objects.get(city_code='CAL', city_state=valle_state)
            male_gender = Gender.objects.get(gender_code='M')
            cc_document = DocumentType.objects.get(document_type_code='CC')
        except (Country.DoesNotExist, State.DoesNotExist, City.DoesNotExist, 
                Gender.DoesNotExist, DocumentType.DoesNotExist) as e:
            self.stdout.write(
                self.style.ERROR(f'Error: Dependencias no encontradas: {e}')
            )
            return

        # Crear usuario solo si no existe
        user_email = 'usuario1@rifas.com'
        if not User.objects.filter(email=user_email).exists():
            regular_user = User.objects.create_user(
                email=user_email,
                password='usuario123',
                first_name='Juan Carlos',
                last_name='Pérez González',
                gender=male_gender,
                document_type=cc_document,
                document_number='1234567890',
                phone_number='3001234567',
                address='Calle 10 #20-30, Cali',
                city=cali_city,
                is_staff=False,
                is_admin=False,
                is_superuser=False
            )
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Usuario creado: {regular_user.email}')
            )
            self.stdout.write(
                self.style.WARNING(f'  🔑 Password: usuario123 (¡CAMBIAR EN PRODUCCIÓN!)')
            )
        else:
            self.stdout.write(f'  ⚠️  Usuario ya existe: {user_email}')

    def create_user1_payment_method(self):
        """Crear método de pago para el usuario regular"""
        self.stdout.write('Creando método de pago para usuario regular...')
        
        try:
            regular_user = User.objects.get(document_number='1234567890')
            debit_card_type = PaymentMethodType.objects.get(payment_method_type_code='TDEB')
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('  ❌ Error: Usuario regular no encontrado')
            )
            return
        except PaymentMethodType.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('  ❌ Error: Tipo de método de pago TDEB no encontrado')
            )
            return
        
        # Verificar si ya existe
        if regular_user.payment_methods.filter(payment_method_type=debit_card_type).exists():
            self.stdout.write('  ⚠️  Método de pago usuario regular ya existe')
            return
            
        # Importar módulos necesarios
        from datetime import date, timedelta
        from django.contrib.auth.hashers import make_password
        from userInfo.models import PaymentMethod
        
        card_number = '4532123456789012'  # Número de tarjeta visa de prueba
        expiration = date.today() + timedelta(days=365*3)
        
        payment_method = PaymentMethod.objects.create(
            user=regular_user,
            payment_method_type=debit_card_type,
            paymenth_method_holder_name='Juan Carlos Pérez González',
            paymenth_method_card_number_hash=make_password(card_number),
            paymenth_method_expiration_date=expiration,
            last_digits=card_number[-4:],
            payment_method_balance=5000000.00,  # 5 millones de saldo inicial
            payment_method_is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Método de pago creado para usuario regular - Saldo: ${payment_method.payment_method_balance:,.0f}')
        )