from app import db

class Responsible(db.Model):
    __tablename__ = "responsible"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), nullable=True, unique=True)  # ID del Docker
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    participant = db.relationship('Participant', backref=db.backref('responsibles', lazy=True))
    name = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Responsible {self.name}>"

    def authenticate(self, dni):
        return self.dni == dni
    
    def logout(self):
        pass
    
    def recoverPassword(self):
        pass
    
    def editProfile(self):
        pass
