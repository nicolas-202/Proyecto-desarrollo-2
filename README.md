# Proyecto-desarrollo-2
Proyecto realizado para la clase de desarrollo de software 2

## Proceso de instalación
## 🚀 Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Python](https://www.python.org/downloads/) (solo para generar la llave secreta)

## 📥 Instalación y configuración

1. **Clonar el repositorio**
```powershell 
git clone https://github.com/nicolas-202/Proyecto-desarrollo-2.git
```
2.**Entrar a la carpeta del proyecto**
```powershell 
cd proyecto-desarrollo-2
```
3.**Configurar variables de entorno**
clonar archivo .env
```powershell
cp .env.example .env
```
crear llave secreta para la aplicación
```powershell
python -c "import secrets; print(secrets.token_hex(25))"
```
editar el archivo .env con la llave generada y actualizar la información de la bd antes de levantar los contenedores.
4.**construir y levantar los contenedores** 
```powershell
docker-compose build
docker-compose up -d
```

## COMANDOS UTILES (NO SON NECESARIOS PARA LA INSTALACIÓN)
1. **DETENER LOS CONTENEDORES**
```powershell
docker-compose down
```
2. **EJECUTAR MIGRACIONES EN DJANGO**
```powershell
docker-compose exec backend python manage.py migrate
```
