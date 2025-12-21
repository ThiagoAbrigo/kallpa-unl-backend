from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    db.init_app(app)
    
    # Inicializar Marshmallow
    from app.schemas import ma
    ma.init_app(app)
    
    with app.app_context():
        from app import models
        db.create_all()
        
        # Register blueprints
        from app.routes.user_routes import user_bp
        app.register_blueprint(user_bp, url_prefix='/api')
        from app.routes.attendance_routes import attendance_bp
        app.register_blueprint(attendance_bp, url_prefix='/api')
        from app.routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api')

    return app
