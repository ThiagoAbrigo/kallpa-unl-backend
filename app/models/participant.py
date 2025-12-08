from app import db

class Participant(db.Model):
    __tablename__ = "participant"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    assessments = db.relationship('Assessment', backref='participant', lazy=True)
    attendances = db.relationship('Attendance', backref='participant', lazy=True)

    def __repr__(self):
        return f"<Participante {self.nombre} {self.apellido}>"
    
    
    def autenticar(self, correo, dni):
        return self.correo == correo and self.dni == dni
    def cerrarSesion(self):
        pass
    def recuperarContraseña(self):
        pass
    def editarPerfil(self):
        pass