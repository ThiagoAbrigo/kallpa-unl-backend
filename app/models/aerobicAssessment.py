from app.models.assessment import Assessment
from app import db

class AerobicAssessment(Assessment):
    __tablename__ = 'aerobic_assessment'
    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    cooper_test_distance = db.Column(db.Integer)
    navette_test_level = db.Column(db.Integer)
    resting_heart_rate = db.Column(db.Integer)
    post_exercise_heart_rate = db.Column(db.Integer)
    
    __mapper_args__ = {
        'polymorphic_identity': 'aerobic_assessment',
    }
