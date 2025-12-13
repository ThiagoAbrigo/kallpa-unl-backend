from app.models.assessment import Assessment
from app import db

class InitialAssessment(Assessment):
    __tablename__ = 'initial_assessment'
    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    cooper_test_distance = db.Column(db.Integer)
    navette_test_level = db.Column(db.Integer)
    resting_heart_rate = db.Column(db.Integer)
    post_exercise_heart_rate = db.Column(db.Integer)
    
    __mapper_args__ = {
        'polymorphic_identity': 'initial_assessment',
    }
    def save_aerobic_results(self):
        db.session.add(self)
        db.session.commit()
    def edit_aerobic_results(self, cooper_test_distance, navette_test_level, resting_heart_rate, post_exercise_heart_rate):
        self.cooper_test_distance = cooper_test_distance
        self.navette_test_level = navette_test_level
        self.resting_heart_rate = resting_heart_rate
        self.post_exercise_heart_rate = post_exercise_heart_rate
        db.session.commit()
    def __repr__(self):
        return f"<InitialAssessment {self.id} - Participant {self.participant_id}>"
