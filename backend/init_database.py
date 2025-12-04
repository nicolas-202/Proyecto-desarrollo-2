#!/usr/bin/env python
"""
Script de inicialización de datos base para el Sistema de Rifas
Ejecuta: python init_database.py

Este script inicializa la base de datos con los datos mínimos necesarios
para el funcionamiento del sistema de rifas.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line


def main():
    """Función principal del script"""

    # Configurar Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

    print("🎯 SISTEMA DE RIFAS - INICIALIZADOR DE BASE DE DATOS")
    print("=" * 55)

    # Verificar si hay datos existentes
    from location.models import Country
    from userInfo.models import DocumentType

    has_countries = Country.objects.exists()
    has_doc_types = DocumentType.objects.exists()

    if has_countries or has_doc_types:
        print("⚠️  ADVERTENCIA: Ya existen datos en la base de datos.")
        response = input("¿Deseas recrear todos los datos? (s/N): ")

        if response.lower() in ["s", "si", "y", "yes"]:
            force = True
            print("🔄 Recreando datos...")
        else:
            force = False
            print("➕ Agregando solo datos faltantes...")
    else:
        force = False
        print("🆕 Inicializando base de datos vacía...")

    try:
        # Ejecutar el comando de seeding
        if force:
            execute_from_command_line(["manage.py", "seed_data", "--force"])
        else:
            execute_from_command_line(["manage.py", "seed_data"])

        print("\n" + "=" * 55)
        print("🎉 INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 55)

        # Mostrar información de acceso
        print("\n📋 INFORMACIÓN DE ACCESO:")
        print("   Email: admin@rifas.com")
        print("   Password: admin123")
        print("   ⚠️  IMPORTANTE: Cambiar la contraseña en producción")

        print("\n📊 DATOS INICIALIZADOS:")
        print("   ✅ Ubicaciones (Colombia, departamentos, ciudades)")
        print("   ✅ Tipos de documento (CC, TI, CE, PP, NIT)")
        print("   ✅ Géneros (M, F, Otro, No especificar)")
        print("   ✅ Métodos de pago (Tarjetas, PSE, billeteras)")
        print("   ✅ Tipos de premio (Dinero, vehículos, etc.)")
        print("   ✅ Estados de rifa (Activa, pausada, etc.)")
        print("   ✅ Usuario administrador")

    except Exception as e:
        print(f"\n❌ ERROR durante la inicialización: {e}")
        print("   Verifica que:")
        print("   - La base de datos esté configurada correctamente")
        print("   - Las migraciones estén aplicadas (python manage.py migrate)")
        print("   - El archivo .env tenga las configuraciones correctas")
        sys.exit(1)


if __name__ == "__main__":
    main()
