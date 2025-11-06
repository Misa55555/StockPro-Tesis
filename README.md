# StockPro - Sistema de Punto de Venta y Gestión de Inventario

## Descripción del Proyecto

**StockPro** es un sistema de punto de venta (POS) integral basado en la web, diseñado para optimizar la gestión operativa de comercios minoristas y PyMEs. El proyecto, desarrollado como trabajo final de tesis, utiliza el framework Django para el backend y Bootstrap para un frontend responsivo.

El sistema facilita la gestión interna de inventario, ventas y cierres de caja. Los usuarios se gestionan mediante roles (Administrador, Vendedor y Cliente). No existe portal de cliente en esta versión; la tabla `Cliente` se mantiene únicamente para futura escalabilidad.

---

## Características Principales

* **Gestión de Inventario Profesional:** Control de productos por lotes, manejo de fechas de vencimiento, alertas de stock mínimo y gestión de marcas y categorías.
* **Punto de Venta (POS):** Interfaz ágil para el registro de ventas con búsqueda dinámica de productos.
* **Dashboard de Gestión:** Panel principal con métricas clave como ventas del día, alertas de stock bajo y productos por vencer.
* **Cierres de Caja:** Control de apertura y cierre de caja con registro de movimientos.
* **Gestión Financiera:** Seguimiento de ingresos, egresos y balance general.
* **Importación y Exportación:** Funcionalidades para cargar el inventario masivamente (El cual lo tomamos como escalabilidad ya que al momento no estaria andando) desde archivos Excel y exportar reportes (Funcionando correctamente).
* **Gestión de Roles:** Sistema de permisos para Administrador, Vendedor y Cliente como roles. No hay portal de cliente; la tabla `Cliente` se mantiene para futura escalabilidad.

---

## Tecnologías Utilizadas

* **Backend:** Python 3.10+, Django 5.1.2
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
* **Base de Datos:** SQLite3 (desarrollo), compatible con MySQL/PostgreSQL (producción)
* **Librerías Principales:** 
  - `django-filter` - Filtrado avanzado de datos
  - `openpyxl` - Importación/exportación de archivos Excel
  - `django-select2` - Selectores mejorados con búsqueda
  - `django-htmx` - Interacciones dinámicas sin recargar página

---

## Guía de Instalación y Puesta en Marcha

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

* **Python 3.10 o superior** - [Descargar Python](https://www.python.org/downloads/)
* **pip** - Gestor de paquetes de Python (incluido con Python)
* **git** - Para clonar el repositorio (opcional)
* **Entorno virtual** - Recomendado para aislar dependencias

### Paso 1: Obtener el Código

Clona el repositorio o descarga el código fuente:

```bash
git clone https://github.com/tu-usuario/stockpro.git
cd stockpro
```

O si descargaste un archivo ZIP, extráelo y navega al directorio:

```bash
cd stockpro
```

### Paso 2: Crear y Activar un Entorno Virtual

Es **altamente recomendado** usar un entorno virtual para evitar conflictos de dependencias:

**En Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

Una vez activado, verás `(venv)` al inicio de tu línea de comandos.

### Paso 3: Instalar las Dependencias

Instala todas las librerías necesarias desde `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Nota:** Si tienes problemas instalando `mysqlclient` en Windows, puedes comentar esa línea en `requirements.txt` si solo usarás SQLite para desarrollo.

### Paso 4: Configurar Variables de Entorno (Opcional)

Para producción, es recomendable configurar variables de entorno. Crea un archivo `.env` en la raíz del proyecto (opcional para desarrollo):

```bash
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Paso 5: Configurar la Base de Datos

El proyecto usa **SQLite** por defecto, lo cual es ideal para desarrollo y no requiere configuración adicional.

#### Aplicar las Migraciones

Ejecuta las migraciones para crear todas las tablas necesarias:

```bash
python manage.py migrate
```

Deberías ver una salida similar a:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, stock, usuarios, ventas, pedidos, cierres, finanzas
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### Paso 6: Crear un Superusuario (Administrador)

Crea una cuenta de administrador para acceder al sistema:

```bash
python manage.py createsuperuser
```

Se te pedirá:
- **Username:** Elige un nombre de usuario (ej: `admin`)
- **Email:** Tu correo electrónico (opcional)
- **Password:** Una contraseña segura (mínimo 8 caracteres)

### Paso 7: Cargar Datos Iniciales (Opcional)

Si el proyecto incluye datos de prueba, puedes cargarlos con:

```bash
python manage.py loaddata initial_data.json
```

### Paso 8: Ejecutar el Servidor de Desarrollo

¡Listo! Inicia el servidor de desarrollo de Django:

```bash
python manage.py runserver
```

Deberías ver:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Paso 9: Acceder al Sistema

Abre tu navegador web y accede a:

* **Página Principal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Panel de Administración Django:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* **Dashboard Principal:** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)

Inicia sesión con las credenciales del superusuario que creaste.

---

## Estructura del Proyecto

```
stockpro/
├── applications/          # Aplicaciones Django del proyecto
│   ├── cierres/          # Gestión de cierres de caja
│   ├── dashboard/        # Panel principal y métricas
│   ├── finanzas/         # Control financiero
│   ├── pedidos/          # Gestión de pedidos
│   ├── stock/            # Inventario y productos
│   ├── usuarios/         # Autenticación y perfiles
│   └── ventas/           # Punto de venta
├── stockpro/             # Configuración principal del proyecto
│   ├── settings.py       # Configuración de Django
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuración WSGI
├── templates/            # Plantillas HTML globales
├── manage.py             # Script de gestión de Django
├── requirements.txt      # Dependencias del proyecto
└── db.sqlite3           # Base de datos SQLite (se crea automáticamente)
```

---

## Uso del Sistema

### Roles de Usuario

El sistema maneja tres tipos de usuarios:

1. **Administrador:** Acceso completo a todas las funcionalidades
2. **Vendedor:** Acceso a ventas, inventario y cierres de caja
3. **Cliente:** Rol disponible para identificar clientes dentro del sistema. 

### Funcionalidades Principales

#### 1. Dashboard
- Vista general de métricas del negocio
- Alertas de stock bajo
- Productos próximos a vencer
- Resumen de ventas del día

#### 2. Gestión de Inventario
- Agregar, editar y eliminar productos
- Control de stock por lotes
- Importación masiva desde Excel
- Gestión de categorías y marcas

#### 3. Punto de Venta
- Búsqueda rápida de productos
- Carrito de compras
- Registro de ventas
- Impresión de tickets


#### 4. Cierres de Caja
- Apertura de caja
- Registro de movimientos
- Cierre y arqueo

---

## Comandos Útiles

### Gestión de la Base de Datos

```bash
# Crear nuevas migraciones después de cambios en modelos
python manage.py makemigrations

# Aplicar migraciones pendientes
python manage.py migrate

# Resetear la base de datos (¡CUIDADO! Borra todos los datos)
python manage.py flush
```

### Gestión de Usuarios

```bash
# Crear un superusuario
python manage.py createsuperuser

# Cambiar contraseña de un usuario
python manage.py changepassword nombre_usuario
```

### Desarrollo

```bash
# Ejecutar el servidor en un puerto específico
python manage.py runserver 8080

# Ejecutar el servidor accesible desde la red local
python manage.py runserver 0.0.0.0:8000

# Abrir shell interactivo de Django
python manage.py shell

# Recopilar archivos estáticos (para producción)
python manage.py collectstatic
```

---

## Solución de Problemas Comunes

### Error: "No module named 'django'"
**Solución:** Asegúrate de haber activado el entorno virtual y ejecutado `pip install -r requirements.txt`

### Error al instalar mysqlclient en Windows
**Solución:** Si solo usarás SQLite, comenta la línea `mysqlclient==2.2.7` en `requirements.txt`

### El servidor no inicia
**Solución:** Verifica que el puerto 8000 no esté en uso. Usa `python manage.py runserver 8080` para usar otro puerto

### Error de migraciones
**Solución:** Ejecuta `python manage.py migrate` para aplicar todas las migraciones pendientes

### Olvidé la contraseña del superusuario
**Solución:** Ejecuta `python manage.py changepassword tu_usuario` para cambiarla

---

## Configuración para Producción

Para desplegar en producción, considera:

1. **Cambiar a una base de datos robusta** (PostgreSQL o MySQL)
2. **Configurar `DEBUG = False`** en `settings.py`
3. **Establecer `ALLOWED_HOSTS`** correctamente
4. **Usar un servidor WSGI** como Gunicorn o uWSGI
5. **Configurar un servidor web** como Nginx o Apache
6. **Usar HTTPS** con certificados SSL
7. **Configurar archivos estáticos** con `collectstatic`
8. **Establecer variables de entorno** para datos sensibles

---

## Licencia

Este proyecto fue desarrollado como trabajo final de tesis. Todos los derechos reservados.

---

## Contacto

Para consultas sobre el proyecto, contacta a través del repositorio o correo electrónico de los autores
misa132456@gmail.com

