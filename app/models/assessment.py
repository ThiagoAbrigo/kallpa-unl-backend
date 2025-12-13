from app import db
from datetime import datetime

class Assessment(db.Model):
    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    waist_circumference = db.Column(db.Float, nullable=False)
    wingspan = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'assessment',
        'polymorphic_on': type
    }

    def calculate_bmi(self):
        if self.height > 0:
            self.bmi = self.weight / (self.height ** 2)
        else:
            self.bmi = 0

    def save_results(self):
        db.session.add(self)
        db.session.commit()

    def edit_results(self, date, weight, height, waist_circumference, wingspan):
        self.date = date
        self.weight = weight
        self.height = height
        self.waist_circumference = waist_circumference
        self.wingspan = wingspan
        self.calculate_bmi()
        db.session.commit()