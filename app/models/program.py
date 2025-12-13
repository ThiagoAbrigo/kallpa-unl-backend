#Esta clase Programa tiene dos valores el id y nombre y se relaciona de 1 a * con horario , pero horario es una composicion de programa es decir que horario contiene programa

from app import db
from datetime import datetime

class Program(db.Model):
    __tablename__ = "program"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    schedules = db.relationship('Schedule', backref='program', lazy=True, cascade="all, delete-orphan")
    def __repr__(self):
        return f"<Program {self.name}>"
    
                               