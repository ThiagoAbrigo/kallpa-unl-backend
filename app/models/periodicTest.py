from app.models.assessment import Assessment
from app import db

class PeriodicTest(Assessment):
    __tablename__ = "periodic_test"

    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    burpees = db.Column(db.Integer, nullable=False)
    squats = db.Column(db.Integer, nullable=False)
    verticalJump = db.Column(db.Integer, nullable=False)
    plank = db.Column(db.Integer, nullable=False)
    pullUps = db.Column(db.Integer, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'periodic_test',
    }
