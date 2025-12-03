from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from app.models import attendance, participant, program, responsible, schedule
        from app.models import assessment, initialAssessment, aerobicAssessment, periodicTest
        
        db.create_all()
        
        # Register blueprints
        from app.routes.attendance_routes import attendance_bp
        app.register_blueprint(attendance_bp, url_prefix='/api')

    return app
