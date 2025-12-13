from app import db
from datetime import datetime

class Participant(db.Model):
    __tablename__ = "participant"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    assessments = db.relationship('Assessment', backref='participant', lazy=True)
    attendances = db.relationship('Attendance', backref='participant', lazy=True)

    def __repr__(self):
        return f"<Participant {self.first_name} {self.last_name}>"
    
    
    def autenticar(self, correo, dni):
        return self.correo == correo and self.dni == dni
    def cerrarSesion(self):
        pass
    def recuperarContraseña(self):
        pass
    def editarPerfil(self):
        pass