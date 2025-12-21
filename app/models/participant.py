from app import db

class Participant(db.Model):
    __tablename__ = "participant"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), nullable=True, unique=True)  # ID del Docker
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    assessments = db.relationship('Assessment', backref='participant', lazy=True)
    attendances = db.relationship('Attendance', backref='participant', lazy=True)

    def __repr__(self):
        return f"<Participant {self.firstName} {self.lastName}>"
    
    def authenticate(self, email, dni):
        return self.email == email and self.dni == dni
    
    def logout(self):
        pass
    
    def recoverPassword(self):
        pass
    
    def editProfile(self):
        pass
