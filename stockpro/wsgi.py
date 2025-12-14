# stockpro/wsgi.py

"""
Configuración WSGI para el proyecto StockPro.

Este módulo expone el callable WSGI como una variable de nivel de módulo llamada ``application``.
Es el punto de entrada estándar para servidores web compatibles con WSGI (Web Server Gateway Interface)
como Gunicorn o uWSGI, utilizados para desplegar la aplicación en entornos de producción síncronos.

Para más información sobre este archivo, consulte:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Establece la variable de entorno por defecto para la configuración de Django.
# Define qué archivo de configuración (settings.py) debe cargar el servidor
# al iniciar la aplicación.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpro.settings')

# Inicializa la aplicación WSGI.
# Esta instancia 'application' es la interfaz que utiliza el servidor web
# para comunicar las solicitudes HTTP al framework Django.
application = get_wsgi_application()