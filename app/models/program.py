#Esta clase Programa tiene dos valores el id y nombre y se relaciona de 1 a * con horario , pero horario es una composicion de programa es decir que horario contiene programa

from app import db

class Program(db.Model):
    __tablename__ = "program"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    horarios = db.relationship('Horario', backref='programa', lazy=True, cascade= "all, delete-orphan")
    def __repr__(self):
        return f"<Programa {self.nombre}>"
    
                               