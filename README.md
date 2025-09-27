# StockPro - Sistema de Punto de Venta y Gestión de Inventario

## Descripción del Proyecto

**StockPro** es un sistema de punto de venta (POS) integral basado en la web, diseñado para optimizar la gestión operativa de comercios minoristas y PyMEs. El proyecto, desarrollado como trabajo final de tesis, utiliza el framework Django para el backend y Bootstrap para un frontend responsivo.

[cite_start]El sistema no solo facilita la gestión interna de inventario, ventas y cierres de caja, sino que también introduce un innovador portal de cliente para la reserva de productos y la consulta de historial de compras, creando un canal de fidelización directo con el consumidor final. [cite: 11]

---

## Características Principales

* **Gestión de Inventario Profesional:** Control de productos por lotes, manejo de fechas de vencimiento, alertas de stock mínimo y gestión de marcas y categorías.
* **Punto de Venta (POS):** Interfaz ágil para el registro de ventas (próxima implementación).
* [cite_start]**Portal de Cliente:** Sistema de login para clientes, historial de compras y funcionalidad de reserva de productos. [cite: 53]
* [cite_start]**Dashboard de Gestión:** Panel principal con métricas clave como ventas del día, alertas de stock bajo y productos por vencer. [cite: 278]
* **Importación y Exportación:** Funcionalidades para cargar el inventario masivamente desde un archivo Excel y exportar reportes.
* [cite_start]**Gestión de Roles:** Sistema de permisos diferenciado para Administradores, Vendedores y Clientes. [cite: 25]

---

## Tecnologías Utilizadas

* **Backend:** Python 3, Django 5.2
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
* [cite_start]**Base de Datos:** SQLite3 (para desarrollo), compatible con MySQL. [cite: 100]
* **Librerías Clave:** `django-filter`, `openpyxl`, `django-select2`.

---

## Guía de Instalación y Puesta en Marcha

Sigue estos pasos para configurar y ejecutar el proyecto en un entorno de desarrollo local.

### 1. Prerrequisitos

* Python 3.10 o superior.
* `pip` (gestor de paquetes de Python).
* `git` (para clonar el repositorio).

### 2. Clonar el Repositorio

```bash
git clone [URL_DE_TU_REPOSITORIO_EN_GITHUB]
cd nombre-del-directorio-del-proyecto
```

### 3. Crear y Activar un Entorno Virtual

Es una buena práctica aislar las dependencias del proyecto.

```bash
# Crear el entorno
python3 -m venv env

# Activar en Linux/macOS
source env/bin/activate

# Activar en Windows
.\env\Scripts\activate
```

### 4. Instalar Dependencias

Instala todas las librerías necesarias listadas en `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Configuración de la Base de Datos

El proyecto está configurado por defecto para usar **SQLite**, que no requiere configuración adicional. Si deseas usar **MySQL**, deberás:
1.  Instalar el conector: `pip install mysqlclient`.
2.  Modificar el archivo `stockpro/settings.py` con tus credenciales de MySQL.

### 6. Aplicar Migraciones

Este comando creará la base de datos y todas las tablas necesarias.

```bash
python manage.py migrate
```

### 7. Crear un Superusuario

Necesitarás una cuenta de administrador para acceder al panel de gestión.

```bash
python manage.py createsuperuser
```
Sigue las instrucciones en la terminal para crear tu usuario.

### 8. Ejecutar el Servidor de Desarrollo

¡Todo listo! Inicia el servidor.

```bash
python manage.py runserver
```
El sistema estará disponible en `http://127.0.0.1:8000/`.

---

## Uso del Sistema

* **Panel de Administración de Django:** Accede en `http://127.0.0.1:8000/admin/` con tu cuenta de superusuario. Aquí puedes gestionar todos los modelos de bajo nivel.
* **Dashboard Principal:** Accede en `http://127.0.0.1:8000/dashboard/`. Esta es la interfaz principal para Administradores y Vendedores.
