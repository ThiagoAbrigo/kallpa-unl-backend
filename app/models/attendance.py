from app import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    
    class Estado:
        PRESENTE = "presente"
        AUSENTE = "ausente"

