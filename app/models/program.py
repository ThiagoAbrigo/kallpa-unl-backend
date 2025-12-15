from app import db

class Program(db.Model):
    __tablename__ = "program"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    
    # CORRECCIÓN AQUÍ: Cambiamos 'Horario' por 'Schedule'
    schedules = db.relationship('Schedule', backref='program', lazy=True)

    def __repr__(self):
        return f"<Program {self.nombre}>"
    
                               