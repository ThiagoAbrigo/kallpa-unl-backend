from app.models.assessment import Assessment
from app import db

class AerobicAssessment(Assessment):
    __tablename__ = 'aerobic_assessment'
    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    cooperTestDistance = db.Column(db.Integer)
    navetteTestLevel = db.Column(db.Integer)
    restingHeartRate = db.Column(db.Integer)
    postExerciseHeartRate = db.Column(db.Integer)
    
    __mapper_args__ = {
        'polymorphic_identity': 'aerobic_assessment',
    }
