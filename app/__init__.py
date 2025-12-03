from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar BD
    db.init_app(app)
    
    # Inicializar Marshmallow
    from app.schemas import ma
    ma.init_app(app)

    # Registrar blueprints
    from app.routes.user_routes import user_bp
    from app.routes.attendance_routes import attendance_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(attendance_bp)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app
