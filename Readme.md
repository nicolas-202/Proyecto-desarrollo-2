# Sistema de Gestión de Rifas Plus 🎫

![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.13.7-blue)
![React](https://img.shields.io/badge/React-18.x-61dafb)
![Node.js](https://img.shields.io/badge/Node.js-22.20.0-339933)
![MariaDB](https://img.shields.io/badge/MariaDB-11.8.3-003545)

¡Bienvenido al Sistema de Gestión de Rifas Plus! Una plataforma web completa y moderna para la administración integral de rifas y sorteos. Este sistema permite gestionar rifas, usuarios, tickets, interacciones y mucho más, con un enfoque en la seguridad, escalabilidad y experiencia de usuario.

> 🚀 **Estado del proyecto**: Sistema en producción, totalmente funcional y desplegado en Render.

Este proyecto fue desarrollado utilizando metodologías ágiles, arquitectura REST API, y mejores prácticas de desarrollo de software, convirtiéndolo en una solución robusta y profesional para la gestión de rifas en línea.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Características Destacadas](#-características-destacadas)
- [Tecnologías y Stack](#-tecnologías-y-stack)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración](#️-instalación-y-configuración)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Migraciones de Base de Datos](#-migraciones-de-base-de-datos)
- [Actualización del Proyecto](#-actualización-del-proyecto)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [CI/CD](#-cicd)
- [Buenas Prácticas](#-buenas-prácticas)
- [Documentación Adicional](#-documentación-adicional)
- [Equipo de Desarrollo](#-equipo-de-desarrollo)
- [Licencia](#-licencia)

---

## 📝 Descripción del Proyecto

**RifaPlus** es un sistema web integral para la gestión de rifas y sorteos en línea. Permite a administradores crear y gestionar rifas, a usuarios comprar tickets, visualizar sorteos en tiempo real, y ofrece funcionalidades avanzadas como:

- Gestión completa de usuarios con roles y permisos
- Administración de rifas con diferentes tipos de premios
- Sistema de compra y gestión de tickets
- Procesamiento automático de rifas y sorteos
- Dashboard administrativo con métricas y estadísticas
- Sistema de notificaciones y reembolsos
- API REST completa para integración con otras plataformas

### 🎯 Objetivo

Desarrollar un sistema web robusto y escalable que facilite la gestión completa del ciclo de vida de rifas, desde la creación hasta la selección de ganadores, implementando las mejores prácticas de desarrollo, arquitectura modular y enfoque DevOps.

---

## ✨ Características Destacadas

- 🔐 **Sistema de Autenticación Seguro**: Registro, login, JWT tokens, roles y permisos granulares
- 🎫 **Gestión de Rifas**: CRUD completo de rifas con múltiples tipos de premios y estados
- 🎟️ **Sistema de Tickets**: Compra, validación, historial y gestión automatizada
- 💰 **Procesamiento de Pagos**: Integración con métodos de pago y sistema de reembolsos 
- 🌍 **Gestión de Ubicaciones**: Países, estados, ciudades con relaciones jerárquicas
- 🧪 **Alta Cobertura de Tests**: Tests unitarios y de integración con pytest
- 🚀 **CI/CD Completo**: GitHub Actions, pre-commit hooks, despliegue automático
- 📱 **Diseño Responsive**: Interfaz moderna y adaptable a todos los dispositivos
- 🔒 **Seguridad Avanzada**: Análisis de seguridad con Bandit, validaciones robustas
- 📦 **Arquitectura Modular**: Apps Django bien organizadas y desacopladas

---

## 🚀 Tecnologías y Stack

### Backend

- **Framework**: Django 4.2 (Python 3.13.7)
- **ORM**: Django ORM con migraciones automáticas
- **API**: Django REST Framework (API RESTful)
- **Base de Datos**: MariaDB 11.8.3+ / MySQL (Producción) | SQLite (Desarrollo)
- **Autenticación**: JWT Tokens + Django Session
- **Testing**: pytest, pytest-django
- **Code Quality**: Bandit (análisis de seguridad), flake8, black

### Frontend

- **Framework**: React 18.x + Vite
- **UI Library**: Material-UI / Bootstrap
- **State Management**: Context API / Redux
- **HTTP Client**: Axios
- **Build Tool**: Vite (Hot Module Replacement)

### DevOps & Infraestructura

- **Control de Versiones**: Git + GitHub
- **CI/CD**: GitHub Actions (tests automáticos + análisis de seguridad)
- **Hosting**: Render (Web Service + PostgreSQL)
- **Servidor**: Gunicorn (WSGI Server)
- **Proxy**: Nginx (en producción)
- **Base de Datos Cloud**: Render PostgreSQL / Supabase
- **Sistema Operativo**: Ubuntu / Windows con WSL2
- **Editor**: Visual Studio Code
- **Gestores de Paquetes**: pip (Python) + npm (Node.js)
- **Contenedores**: Docker + Docker Compose

### 🔗 Enlace Despliegue

🌐 **Aplicación en Producción**: [https://frontend-rifaplus.onrender.com](https://frontend-rifaplus.onrender.com)

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas en tu equipo:

### Herramientas Básicas

- **Git**: >= 2.30 (Para clonar el repositorio y gestionar el código fuente)
- **Python**: >= 3.13.7 (Recomendado para ejecutar el backend)
- **Node.js**: >= 22.20.0 y npm (Para manejar paquetes de JavaScript y frontend)
- **Editor de Código**: Visual Studio Code (recomendado)

### Sistema de Base de Datos

- **XAMPP** (RECOMENDADO): Con MariaDB >= 11.8.3
  - O alternativamente **MySQL** >= 8.0
  - O **PostgreSQL** >= 13 (para producción)

### Herramientas Opcionales

- **Docker** + **Docker Compose**: Para ejecución en contenedores
- **Postman**: Para testing de API
- **Git Bash** / **WSL2**: Para mejor experiencia en Windows

---

## 🛠️ Instalación y Configuración

### Instalación Completa (Primera Vez)

#### 1. Clonar el Repositorio

Primero debes hacer un **fork** del repositorio, luego clona tu fork en tu dispositivo:

```powershell
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY
cd proyecto-desarrollo-2
```

#### 2. Configurar el Backend (Django)

Navega a la carpeta backend y crea un entorno virtual:

```powershell
cd backend
python -m venv venv

# Activar el entorno virtual (Windows)
venv\Scripts\activate

# Activar el entorno virtual (Mac/Linux)
source venv/bin/activate
```

Instala las dependencias de Python:

```powershell
pip install -r requirements.txt
```

#### 3. Configurar Variables de Entorno

Copia el archivo de ejemplo y configúralo:

```powershell
cp .env.example .env
```

Genera una SECRET_KEY para Django:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y pégalo en la variable `SECRET_KEY` de tu archivo `.env`. Luego modifica las demás variables según tu configuración local (base de datos, URLs, etc.).

#### 4. Configurar la Base de Datos

Asegúrate de que XAMPP/MySQL/MariaDB esté corriendo. Luego ejecuta las migraciones:

```powershell
# Crear migraciones
python manage.py makemigrations location userInfo user interactions raffleInfo raffle tickets

# Aplicar migraciones
python manage.py migrate
```

Poblar la base de datos con datos iniciales:

```powershell
python manage.py seed_data
```

#### 5. Configurar el Frontend (React)

En una nueva terminal, navega a la carpeta frontend:

```powershell
cd frontend
npm install
```

#### 6. Ejecutar el Proyecto

**Backend (Django):**
```powershell
# Desde la carpeta backend con el entorno virtual activado
python manage.py runserver
```

El backend estará disponible en: `http://localhost:8000`

**Frontend (React + Vite):**
```powershell
# Desde la carpeta frontend en otra terminal
npm run dev
```

El frontend estará disponible en: `http://localhost:5173` (o el puerto que indique Vite)

#### 7. Acceder al Sistema

Credenciales de acceso por defecto:
- **Email**: admin@rifas.com
- **Contraseña**: admin123

---

## 📁 Estructura del Proyecto

```
proyecto-desarrollo-2/
├── backend/                      # Backend Django
│   ├── core/                     # Configuración principal del proyecto
│   │   ├── settings.py          # Configuración de Django
│   │   ├── urls.py              # URLs principales
│   │   ├── wsgi.py              # WSGI para producción
│   │   └── asgi.py              # ASGI para WebSockets
│   ├── location/                 # App de ubicaciones (países, estados, ciudades)
│   │   ├── models.py
│   │   ├── serializer.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── user/                     # App de usuarios
│   │   ├── models.py
│   │   ├── serializer.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── userInfo/                 # Información adicional de usuarios
│   ├── raffle/                   # App de rifas
│   │   ├── models.py
│   │   ├── serializer.py
│   │   ├── views.py
│   │   ├── signals.py           # Señales para automatización
│   │   └── management/          # Comandos personalizados
│   ├── raffleInfo/               # Información de rifas
│   ├── tickets/                  # App de tickets
│   ├── interactions/             # Interacciones de usuarios
│   ├── permissions/              # Permisos personalizados
│   ├── tests/                    # Tests unitarios y de integración
│   │   ├── test_user.py
│   │   ├── test_raffle.py
│   │   ├── test_ticket.py
│   │   └── ...
│   ├── media/                    # Archivos subidos (imágenes de rifas)
│   ├── manage.py                 # CLI de Django
│   ├── requirements.txt          # Dependencias Python
│   ├── pytest.ini               # Configuración de pytest
│   ├── Dockerfile               # Docker para backend
│   └── bandit-report.json       # Reporte de seguridad
├── frontend/                     # Frontend React + Vite
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   ├── pages/               # Páginas/Vistas
│   │   ├── services/            # Servicios API (Axios)
│   │   ├── contexts/            # Context API
│   │   ├── hooks/               # Custom hooks
│   │   ├── styles/              # Estilos CSS/SCSS
│   │   ├── utils/               # Utilidades
│   │   ├── App.jsx             # Componente principal
│   │   └── main.jsx            # Entry point
│   ├── public/                  # Archivos estáticos
│   ├── package.json            # Dependencias npm
│   ├── vite.config.js          # Configuración Vite
│   ├── Dockerfile              # Docker para frontend
│   └── nginx.conf              # Configuración Nginx
├── docker-compose.yml           # Orquestación de contenedores
├── SETUP.md                     # Guía de configuración
├── DEPLOY_SETUP.md             # Guía de despliegue
└── README.md                    # Este archivo
```

---

## 🗄️ Migraciones de Base de Datos

### Crear Nuevas Migraciones

Cuando realices cambios en los modelos, crea las migraciones:

```powershell
python manage.py makemigrations
```

### Aplicar Migraciones

Para aplicar las migraciones a la base de datos:

```powershell
python manage.py migrate
```

### Crear Migraciones para Apps Específicas

```powershell
python manage.py makemigrations location userInfo user interactions raffleInfo raffle tickets
```

### Ver el Estado de las Migraciones

```powershell
python manage.py showmigrations
```

### Revertir Migraciones

```powershell
python manage.py migrate app_name migration_name
```

---

## 🔄 Actualización del Proyecto

Si ya tienes el proyecto instalado y necesitas actualizarlo con los últimos cambios:

### 1. Sincronizar Fork

Sincroniza tu fork con el repositorio original desde GitHub.

### 2. Traer Cambios

```powershell
git pull origin main
```

### 3. Actualizar Dependencias Backend

```powershell
cd backend
pip install -r requirements.txt
```

### 4. Actualizar Dependencias Frontend

```powershell
cd frontend
npm install
```

### 5. Limpiar Migraciones (Si es Necesario)

Si hay conflictos con migraciones, puedes eliminarlas y recrearlas:

```powershell
# Ejecutar desde la carpeta backend
$apps = @("location", "raffle", "raffleInfo", "tickets", "user", "userInfo", "interactions")
foreach ($app in $apps) {
    $migrationPath = "$app\migrations"
    if (Test-Path $migrationPath) {
        $migrationFiles = Get-ChildItem -Path $migrationPath -File -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" }
        if ($migrationFiles) {
            $migrationFiles | Remove-Item -Force
            Write-Host "Migraciones eliminadas en $app ($($migrationFiles.Count) archivos)"
        }
    }
}
```

### 6. Crear Nueva Base de Datos

Crea una nueva base de datos y actualiza el nombre en tu archivo `.env`.

### 7. Recrear Migraciones

```powershell
python manage.py makemigrations location userInfo user interactions raffleInfo raffle tickets
python manage.py migrate
```

### 8. Poblar Base de Datos

```powershell
python manage.py seed_data
```

### 9. Verificar Funcionamiento

```powershell
# Terminal 1 - Backend
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🧪 Testing

El proyecto incluye una suite completa de tests unitarios y de integración.

### Ejecutar Todos los Tests

```powershell
# Desde la carpeta backend
pytest
```

### Ejecutar Tests con Cobertura

```powershell
pytest --cov=. --cov-report=html
```

### Ejecutar Tests Específicos

```powershell
# Tests de un archivo específico
pytest tests/test_user.py

# Tests de una función específica
pytest tests/test_raffle.py::test_create_raffle
```

### Tests Disponibles

- `test_user.py` - Tests de gestión de usuarios
- `test_raffle.py` - Tests de rifas
- `test_ticket.py` - Tests de tickets
- `test_interaction.py` - Tests de interacciones
- `test_auto_raffle_processing.py` - Tests de procesamiento automático
- `test_refund_functionality.py` - Tests de reembolsos
- Y muchos más...

### Análisis de Seguridad

El proyecto utiliza Bandit para análisis de seguridad:

```powershell
bandit -r . -f json -o bandit-report.json
```

---

## 🚀 Despliegue

### Despliegue en Render

El proyecto está configurado para despliegue automático en Render.

#### Configuración de Render (Backend)

1. **Build Command**:
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```

2. **Start Command**:
   ```bash
   gunicorn core.wsgi:application
   ```

3. **Variables de Entorno**:
   - `SECRET_KEY`: Django secret key
   - `DEBUG`: False (en producción)
   - `ALLOWED_HOSTS`: Tu dominio de Render
   - `DATABASE_URL`: URL de la base de datos
   - Variables de configuración adicionales

#### Configuración de Render (Frontend)

1. **Build Command**:
   ```bash
   npm install && npm run build
   ```

2. **Start Command**:
   ```bash
   npm run preview
   ```

### Despliegue con Docker

```powershell
# Construir y ejecutar con Docker Compose
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

---

## 🔄 CI/CD

### GitHub Actions

El proyecto incluye workflows de GitHub Actions para CI/CD:

- **Tests Automáticos**: Se ejecutan en cada push y PR
- **Análisis de Seguridad**: Bandit se ejecuta automáticamente
- **Linting**: Verificación de código con flake8
- **Despliegue Automático**: A Render en merge a main

### Pre-commit Hooks

Para añadir validaciones locales antes de cada commit:

```powershell
# Desde la raíz del proyecto
cp .github/scripts/pre-commit-check.sh .git/hooks/pre-commit
```

Esto ejecutará:
- Verificación de formato de código
- Tests unitarios
- Análisis de seguridad básico

---

## 📏 Buenas Prácticas

### Workflow de Desarrollo

1. **Crear una Rama**: Para cada nueva funcionalidad o corrección
   ```powershell
   git checkout -b feature/nombre-descriptivo
   ```

2. **Commits Descriptivos**: Usa mensajes claros y específicos
   ```powershell
   git commit -m "feat: añadir funcionalidad de reembolsos automáticos"
   ```

3. **Pull Request**: Crea PR hacia `main` o `develop`
   - Describe los cambios realizados
   - Incluye capturas de pantalla si aplica
   - Asegúrate que los tests pasen

### Convención de Commits

Seguimos la convención de Conventional Commits:

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios en documentación
- `style:` - Formato de código (no afecta funcionalidad)
- `refactor:` - Refactorización de código
- `test:` - Añadir o modificar tests
- `chore:` - Tareas de mantenimiento

### Code Style

- **Python**: Seguir PEP 8, usar Black para formateo
- **JavaScript**: Usar ESLint + Prettier
- **Nombres**: Descriptivos y en inglés para código, español para comentarios

---

## 📚 Documentación Adicional

### Documentación del Proyecto

- 📊 **Diagramas**: [Draw.io - Documentación Visual](https://drive.google.com/file/d/1jIydWksU_XRTRXGKeYx1Ogy5hUK8vNoH/view?usp=sharing)
- 📖 **SETUP.md**: Guía detallada de configuración
- 📖 **DEPLOY_SETUP.md**: Guía de despliegue en producción
- 📖 **API Docs**: Documentación de endpoints (próximamente con Swagger)

### Recursos Externos

- [Documentación Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)

---

## 👥 Equipo de Desarrollo

Este proyecto fue desarrollado por estudiantes de Desarrollo de Software 2:

- **[Nicolás Gonzalez Giraldo]** - Product Owner / Developer
- **[Karen Dahiana Isaza Franco]** - Developer
- **[Keiner Alejandro Rivas Chica]** - Developer
- **[Juan Esteban Vergara Restrepo]** - Developer

### Roles y Responsabilidades

- **Product Owner**: Define requisitos, prioriza backlog, valida funcionalidades
- **Scrum Master**: Facilita ceremonias Scrum, elimina impedimentos
- **Development Team**: Implementa funcionalidades, tests, documentación

---

## 📞 Contacto y Soporte

- **Repositorio**: [GitHub](https://github.com/nicolas-202/proyecto-desarrollo-2)
- **Aplicación**: [https://frontend-rifaplus.onrender.com](https://frontend-rifaplus.onrender.com)
- **Issues**: [GitHub Issues](https://github.com/nicolas-202/proyecto-desarrollo-2/issues)

---

## 📄 Licencia

Este proyecto es de uso académico para el curso de Desarrollo de Software 2.

---

**Última actualización**: Diciembre 2024  
**Versión**: 1.0.0
