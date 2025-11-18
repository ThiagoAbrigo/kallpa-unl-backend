# app/config.py

class Config:
    """Configuración base."""
    # Clave de sesión esencial para Flask
    SECRET_KEY = 'clave-secreta-para-kallpa-unl'

class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True