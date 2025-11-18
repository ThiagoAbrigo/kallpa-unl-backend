from flask import Flask
from .config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    """
    Función de fábrica que inicializa la aplicación Flask.
    """
    app = Flask(__name__)
    
    app.config.from_object(config_class)

    return app