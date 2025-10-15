from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        if not password:
            raise ValueError('La contraseña es obligatoria')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        # Asignar grupo "Usuario" por defecto
    
    def create_superuser(self, email, password=None, **extra_fields):
        # Establecer que es superusuario
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        # Validar
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        # Llamar a create_user (SIN username)
        user = self.create_user(email, password, **extra_fields)
        # Asignar grupo "Administrador" por defecto
class User(AbstractBaseUser, PermissionsMixin):
    # Información de autenticación
    email = models.EmailField(max_length=100, unique=True, verbose_name='Correo electrónico')
    # Información personal básica
    first_name = models.CharField(max_length=30, verbose_name='Nombre')
    last_name = models.CharField(max_length=30,  verbose_name='Apellido')
    
    # Campos de control (importantes para Django)
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_staff = models.BooleanField(default=False, verbose_name='Es staff')
    is_admin = models.BooleanField(default=False, verbose_name='Es admin?')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Fecha de registro')
    
    # Relaciones con otros modelos (OPCIONALES para permitir registro simple)
    city = models.ForeignKey(
        'location.City',  # Usa string para evitar importación circular
        on_delete=models.RESTRICT,
        verbose_name='Ciudad'
    )
    gender = models.ForeignKey(
        'userInfo.Gender',
        on_delete=models.RESTRICT,
        verbose_name='Género'
    )
    document_type = models.ForeignKey(
        'userInfo.DocumentType',
        on_delete=models.RESTRICT,
        verbose_name='Tipo de documento'
    )
    document_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de documento'
    )
    phone_number = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Teléfono'
    )
    address = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Dirección'
    )
    
    # Configuración de autenticación
    USERNAME_FIELD = 'email'  # El campo para login
    # CORRECCIÓN: Quitadas las claves foráneas de REQUIRED_FIELDS
    REQUIRED_FIELDS = ['first_name', 'last_name']  
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name