
from app import db      
#The Responsible class relates to Participant Responsible 0..* to 0..1 Participant

class Responsible(db.Model):
    __tablename__ = "responsible"


    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), nullable=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    participant = db.relationship('Participant', backref=db.backref('responsibles', lazy=True))
    name = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

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