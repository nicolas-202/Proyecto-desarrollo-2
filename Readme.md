Dirección del Draw.io que contiene la documentación:
https://drive.google.com/file/d/1jIydWksU_XRTRXGKeYx1Ogy5hUK8vNoH/view?usp=sharing


# Guía de Implementación para Colaboradores
Proyecto: Proyecto-desarrollo-2  
Descripción: Proyecto realizado para la clase de desarrollo de software 2  

---

## 1. **Instalación de Herramientas Básicas**

Antes de comenzar, asegúrate de tener instalados en tu equipo:

- **Git**: Para clonar el repositorio y gestionar el código fuente.
- **Python (recomendado 3.13.7)**: Para ejecutar el backend y scripts.
- **Node.js (22.20.0) y npm**: Para manejar paquetes de JavaScript y herramientas de frontend.
- Un editor de código (VSCode recomendado).
- Sistema de gestion de base de datos **XAMPP (RECOMENDADO)**. Verificar que la versión de Mariadb sea 11.8.3 o superior

## 2. **Configurar git y clonar el repositorio**

primero debes hacer un fork del repositorio, desde allí clonas el repositorio en tu dispositivo usando el comando 

```powershell
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY
```

## 3. **Configurar y Activar el Entorno Virtual en Python**

Para evitar conflictos de dependencias, crea un entorno virtual **dentro de la carpeta backend**:

```powershell
cd backend
python -m venv venv
# Activar el entorno (Windows)
venv\Scripts\activate
# Activar el entorno (Mac/Linux)
source venv/bin/activate
```

## 4. **Instalar Dependencias de Python**

Si existe un archivo `requirements.txt`, instala las dependencias:

```powershell
pip install -r requirements.txt
```

(Si el archivo no existe, consulta al líder del proyecto qué librerías se deben instalar).

## 5. **Configurar Variables de Entorno**

Se debe copiar el archivo .env.example en un archivo .env dentro de la carpeta Backend

```powershell
cp .env.example .env
```
Modifica los valores según tus credenciales/local.

# Obtener secret key

Para obtener la secret key copiar en la terminal el siguiente comando

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copias el resultado y lo pegas en la variable secret key de tu .env
## 6. **Instalar Dependencias de JavaScript**

Debes volver a la carpeta raiz del proyecto y entrar a la carpeta frontend
```powershell
cd ..
cd frontend
npm install
```

## 7. **Ejecutar el Proyecto**

- **Backend (Python):**
  ```powershell
  python manage.py runserver
  ```
- **Frontend (JavaScript):**
  ```powershell
  npm run dev
  ```

## 9. **Verificar la Instalación**

Accede a la dirección local indicada (por ejemplo, `http://localhost:8000` o `http://localhost:5713`) y verifica que la aplicación funcione.

## Buenas practicas
- Para hacer cualquier cambio en la aplicación se debera crear una nueva rama, trabajar en ella y despues hacer merge con la rama master
- Se deben dar nombres descriptivos y claros a los commits, asi como informar de los cambios realizados

# Migraciones

- Para crear migraciones se debe ejecutar el comando 

  ```powershell
  python manage.py makemigrations
  ```

- Para ejecutar migraciones se debe ejecutar el comando 

  ```powershell
  python manage.py migrate
  ```

## Si ya tienes el proyecto instalado

Debes sincronizar tu fork con el repositorio original.
Luego debes de traer los cambios a tu repositorio local con el siguiente comando.

```powershell
git pull origin main
```
Debes instalar de nuevo todas las dependencias en el backend y en el frontend

En la carpeta backend ejecutas: 
```powershell
pip install -r requirements.txt
```
En la carpeta frontend ejecutas: 
```powershell
npm install
```

Se deben eliminar todas las migraciones corriendo el siguiente comando dentro de la carpeta backend
```powershell
$apps = @("location", "raffle", "raffleInfo", "tickets", "user", "userInfo", "interactions"); foreach ($app in $apps) { $migrationPath = "$app\migrations"; if (Test-Path $migrationPath) { $migrationFiles = Get-ChildItem -Path $migrationPath -File -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" }; if ($migrationFiles) { $migrationFiles | Remove-Item -Force; Write-Host "Migraciones eliminadas en $app ($($migrationFiles.Count) archivos)" } else { Write-Host "No hay migraciones para eliminar en $app" } } else { Write-Host "Directorio de migraciones no encontrado en $app" } }
```
Se debe crear una nueva base de datos y cambiar el nombre de la base de datos por el nuevo en tu archivo .env 

Se deben de hacer las migraciones de nuevo, ejecutando estos comandos 

```powershell
python manage.py makemigrations location userInfo user interactions raffleInfo raffle tickets
python manage.py migrate
```
Se debe de poblar la base de datos con el seeder 

```powershell
python manage.py seed_data
```


Probar la inicialización de la aplicación con
  ```powershell
  python manage.py runserver
  ```

En otra terminal ejecutar 
  ```powershell
  npm run dev
  ```

ingresas a la aplicación con
email: admin@rifas.com
contraseña: admin123