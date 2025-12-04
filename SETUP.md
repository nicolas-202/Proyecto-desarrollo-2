# Guía de Configuración del Proyecto

## 📋 Requisitos Previos

- Python 3.13+
- Node.js 18+
- Git
- Acceso al proyecto de Supabase

---

## 🚀 Configuración Inicial

### 1. Clonar el Repositorio

```bash
git clone https://github.com/nicolas-202/Proyecto-desarrollo-2.git
cd Proyecto-desarrollo-2
```

### 2. Configurar Backend (Django)

#### 2.1 Crear entorno virtual

```bash
cd backend
python -m venv venv
```

#### 2.2 Activar entorno virtual

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### 2.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 2.4 Configurar variables de entorno

1. Copia el archivo de ejemplo:
   ```bash
   copy .env.example .env   # Windows
   cp .env.example .env     # Linux/Mac
   ```

2. Edita `backend/.env` con tus credenciales:

   **Obtener credenciales de Supabase:**
   - Ve a [Supabase Dashboard](https://supabase.com/dashboard)
   - Selecciona tu proyecto
   - Settings → Database → **Connection Pooling**
   - Selecciona **"Session mode"** (requerido para IPv4)
   - Copia el connection string y actualiza:

   ```dotenv
   SECRET_KEY='tu-secret-key-unica'
   MYSQL_PASSWORD='tu-password-de-supabase'
   ```

#### 2.5 Aplicar migraciones

```bash
python manage.py migrate
```

#### 2.6 Cargar datos iniciales (opcional)

```bash
python manage.py seed_data
```

#### 2.7 Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

El backend estará disponible en: `http://localhost:8000`

---

### 3. Configurar Frontend (React + Vite)

#### 3.1 Instalar dependencias

```bash
cd ../frontend
npm install
```

#### 3.2 Ejecutar servidor de desarrollo

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

---

## 🔧 Configuración del Git Hook (Pre-commit)

Para ejecutar automáticamente las verificaciones de calidad antes de cada commit:

```bash
# Desde la raíz del proyecto
cp .github/scripts/pre-commit-check.sh .git/hooks/pre-commit
```

El hook ejecutará:
- ✅ **Tests** (bloquean commit si fallan)
- ⚠️ **Pylint** (advertencia)
- ⚠️ **Black** (advertencia)
- ⚠️ **Bandit** (advertencia)
- ⚠️ **ESLint** (advertencia)
- ⚠️ **Prettier** (advertencia)

Para saltar el hook temporalmente:
```bash
git commit --no-verify -m "mensaje"
```

---

## 🧪 Ejecutar Tests

### Backend
```bash
cd backend
pytest
```

### Con cobertura
```bash
pytest --cov
```

---

## 🎨 Formateo de Código

### Backend (Black)
```bash
cd backend
black .
```

### Frontend (Prettier)
```bash
cd frontend
npm run format
```

---

## 🔍 Linting

### Backend (Pylint)
```bash
cd backend
pylint user/ userInfo/ raffle/ raffleInfo/ tickets/ interactions/ location/ permissions/
```

### Frontend (ESLint)
```bash
cd frontend
npm run lint
```

---

## 🔒 Escaneo de Seguridad

```bash
cd backend
bandit -r user/ userInfo/ raffle/ raffleInfo/ tickets/ interactions/ location/ permissions/ -ll
```

---

## 📝 Estructura del Proyecto

```
proyecto-desarrollo-2/
├── backend/              # Django REST API
│   ├── core/            # Configuración principal
│   ├── user/            # Gestión de usuarios
│   ├── raffle/          # Sistema de rifas
│   ├── tickets/         # Gestión de tickets
│   ├── tests/           # Tests unitarios
│   └── requirements.txt
├── frontend/            # React + Vite
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
└── .github/
    └── scripts/
        └── pre-commit-check.sh
```

---

## ⚠️ Notas Importantes

### Base de Datos
- **Usar Session Pooler de Supabase** (no Direct Connection)
- Direct Connection solo soporta IPv6
- Session Pooler es compatible con IPv4 (necesario para la mayoría de redes)

### Seguridad
- **Nunca** commitear el archivo `.env` con credenciales reales
- `.env` está en `.gitignore`
- Usa `.env.example` como plantilla

### Python
- El proyecto usa Python 3.13.7
- Asegúrate de activar el virtualenv antes de trabajar

---

## 🆘 Solución de Problemas

### Error: "could not translate host name"
- Estás usando Direct Connection en vez de Session Pooler
- Cambia a Session Pooler en Supabase Dashboard

### Error: "connection to localhost refused"
- Verifica que `.env` tenga las credenciales correctas
- Revisa que no haya espacios extras en los nombres de variables

### Tests fallan
- Asegúrate de tener la base de datos configurada
- Ejecuta las migraciones: `python manage.py migrate`

### Pre-commit hook no se ejecuta
- Verifica permisos: `chmod +x .git/hooks/pre-commit` (Linux/Mac)
- En Windows, Git Bash maneja permisos automáticamente

---

## 📚 Recursos Adicionales

- [Documentación Django](https://docs.djangoproject.com/)
- [Documentación React](https://react.dev/)
- [Documentación Supabase](https://supabase.com/docs)
- [Guía de Pylint](https://pylint.readthedocs.io/)
- [Guía de ESLint](https://eslint.org/docs/)
