# config.py

import os
from dotenv import load_dotenv 

load_dotenv()

class Config:
    """Configuración base común a todos los entornos"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
         raise ValueError("¡ERROR: No se ha establecido la variable de entorno SECRET_KEY! Es esencial para la seguridad de la sesión.")

    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASEDIR, 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')
    if not GOOGLE_AI_API_KEY:
         print("ADVERTENCIA: La variable de entorno GOOGLE_AI_API_KEY no está configurada. Las funcionalidades de IA podrían no funcionar.") # O puedes lanzar un error si la IA es esencial.


class DevelopmentConfig(Config):
    """Configuración para el entorno de Desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para el entorno de Producción"""

    pass

config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig,
    default=DevelopmentConfig 
)