from app import db

class Horario(db.Model):
    __tablename__ = "horario"

    id = db.Column(db.Integer, primary_key=True)
    programa_id = db.Column(db.Integer, db.ForeignKey('programa.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    diaSemana = db.Column(db.String(20), nullable=False)
    horaInicio = db.Column(db.String(10), nullable=False)
    horaFin = db.Column(db.String(10), nullable=False)
    cuposMaximos = db.Column(db.Integer, nullable=False)
    asistencias = db.relationship('Asistencia', backref='horario', lazy=True)

    def __repr__(self):
        return f"<Horario {self.nombre}>"