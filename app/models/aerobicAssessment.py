from app.models.assessment import Assessment
from app import db

class AerobicAssessment(Assessment):
    __tablename__ = 'aerobic_assessment'
    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    external_id = db.Column(db.String(100), nullable=True)
    cooper_test_distance = db.Column(db.Integer)
    navette_test_level = db.Column(db.Integer)
    resting_heart_rate = db.Column(db.Integer)
    post_exercise_heart_rate = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    __mapper_args__ = {
        'polymorphic_identity': 'aerobic_assessment',
    }
