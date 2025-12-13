
from app import db
from datetime import datetime

class Responsible(db.Model):
    __tablename__ = "responsible"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    participant = db.relationship('Participant', backref=db.backref('responsibles', lazy=True))
    name = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Responsible {self.name}>"
    

    def autenticar(self, dni):
        return self.dni == dni
    
    def cerrarSesion(self):
        pass
    
    def recuperarContraseña(self):
        pass
    
    def editarPerfil(self):
        pass    