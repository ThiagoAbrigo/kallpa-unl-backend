from app.models.assessment import Assessment
from app import db

class PeriodicTest(Assessment):
    __tablename__ = "periodic_test"

    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    burpees = db.Column(db.Integer, nullable=False)
    sentadillas = db.Column(db.Integer, nullable=False)
    saltoVertical = db.Column(db.Integer, nullable=False)
    plancha = db.Column(db.Integer, nullable=False)
    dominadas = db.Column(db.Integer, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'periodic_test',
    }