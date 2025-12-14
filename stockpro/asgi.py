# stockpro/asgi.py

"""
Configuración ASGI para el proyecto StockPro.

Este módulo expone el callable ASGI como una variable de nivel de módulo llamada ``application``.
Es el punto de entrada principal para servidores web compatibles con ASGI (Asynchronous Server Gateway Interface),
permitiendo el despliegue del proyecto en servidores asíncronos y el manejo de conexiones
de larga duración (como WebSockets) si fuera necesario en el futuro.
"""

import os

from django.core.asgi import get_asgi_application

# Establece la variable de entorno por defecto para la configuración de Django.
# Esto asegura que el sistema sepa dónde encontrar la configuración del proyecto (settings.py)
# antes de iniciar la aplicación.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpro.settings')

# Inicializa la aplicación ASGI.
# Esta instancia 'application' es la que utilizan los servidores de aplicaciones (como Uvicorn o Daphne)
# para interactuar con el código de Django.
application = get_asgi_application()