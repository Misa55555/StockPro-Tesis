# stockpro/settings.py

"""
Configuración principal del proyecto Django 'StockPro'.

Este módulo contiene todas las configuraciones a nivel de proyecto, incluyendo:
- Definición de rutas base y estructura de directorios.
- Configuración de seguridad (claves secretas, modo debug, hosts permitidos).
- Registro de aplicaciones instaladas (INSTALLED_APPS), tanto nativas de Django como aplicaciones propias del negocio.
- Configuración de Middleware y capas de procesamiento de solicitudes.
- Configuración de base de datos (SQLite por defecto para desarrollo).
- Configuración de internacionalización y archivos estáticos.
- Definición del modelo de usuario personalizado y rutas de autenticación.

Para más información sobre este archivo, consulte:
https://docs.djangoproject.com/en/5.2/topics/settings/
"""

from pathlib import Path
import os

# Construcción de rutas dentro del proyecto (ej: BASE_DIR / 'subdir').
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ==============================================================================

# Clave secreta para la firma criptográfica.
# ADVERTENCIA: Mantener esta clave secreta en producción.
SECRET_KEY = 'django-insecure-c*9%_9ub5qvyu%htk90_ll0*tg78q&cdk(f&hkvbh4t_*zz*vb'

# Modo de depuración.
# ADVERTENCIA: Nunca ejecutar con DEBUG = True en un entorno de producción.
DEBUG = True

# Lista de cadenas que representan los nombres de dominio/host que este sitio puede servir.
ALLOWED_HOSTS = []


# ==============================================================================
# DEFINICIÓN DE APLICACIONES
# ==============================================================================

INSTALLED_APPS = [
    # Aplicaciones nativas de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicaciones del Proyecto (Módulos de Negocio)
    'applications.usuarios',    # Gestión de usuarios, roles y clientes.
    'applications.stock',       # Gestión de inventario, productos y lotes.
    'applications.ventas',      # Punto de venta (POS) y facturación.
    'applications.cierres',     # Arqueo y cierre de caja.
    'applications.dashboard',   # Panel de control y reportes.
    'applications.finanzas',    # Registro de gastos y KPIs financieros.
    
    # Librerías de Terceros
    'django_select2',           # Widgets de selección mejorados con búsqueda AJAX.
    'django_filters',           # Filtrado avanzado de QuerySets.
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de URLs raíz.
ROOT_URLCONF = 'stockpro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Directorio global de plantillas.
        'APP_DIRS': True, # Busca plantillas dentro de cada aplicación instalada.
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplicación WSGI para servidores web compatibles.
WSGI_APPLICATION = 'stockpro.wsgi.application'


# ==============================================================================
# BASE DE DATOS
# ==============================================================================
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # Base de datos local basada en archivo.
    }
}


# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==============================================================================
# INTERNACIONALIZACIÓN
# ==============================================================================
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ==============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JavaScript, Images)
# ==============================================================================
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Directorios adicionales donde buscar archivos estáticos aparte de los directorios 'static' de cada app.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# ==============================================================================
# CONFIGURACIÓN ADICIONAL
# ==============================================================================

# Tipo de campo de clave primaria por defecto para modelos.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de Usuario Personalizado.
# Se utiliza 'usuarios.Usuario' en lugar del modelo por defecto de Django para extender funcionalidades (roles, etc).
AUTH_USER_MODEL = 'usuarios.Usuario'

# Rutas de redirección para el sistema de autenticación.
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard_app:dashboard' # Redirección tras login exitoso.
LOGOUT_REDIRECT_URL = 'login' # Redirección tras logout.