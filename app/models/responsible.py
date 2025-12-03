
from app import db      

class Responsible(db.Model):
    __tablename__ = "responsible"


    id = db.Column(db.Integer, primary_key=True)
    participante_id = db.Column(db.Integer, db.ForeignKey('participante.id'))
    participante = db.relationship('Participante', backref=db.backref('responsables', lazy=True))
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Responsible {self.nombre}>"
    

    def autenticar(self, dni):
        return self.dni == dni
        
    def cerrarSesion(self):
        pass
    
    def recuperarContraseña(self):
        pass
    
    def editarPerfil(self):
        pass    