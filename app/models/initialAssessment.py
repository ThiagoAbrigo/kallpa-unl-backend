from app.models.assessment import Assessment
from app import db
import uuid


class InitialAssessment(Assessment):
    __tablename__ = "initial_assessment"
    id = db.Column(db.Integer, db.ForeignKey("assessment.id"), primary_key=True)
    external_id = db.Column(
        db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    cooperTestDistance = db.Column(db.Integer)
    navetteTestLevel = db.Column(db.Integer)
    restingHeartRate = db.Column(db.Integer)
    postExerciseHeartRate = db.Column(db.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "initial_assessment",
    }

    def saveAerobicResults(self):
        db.session.add(self)
        db.session.commit()

    def editAerobicResults(
        self,
        cooperTestDistance,
        navetteTestLevel,
        restingHeartRate,
        postExerciseHeartRate,
    ):
        self.cooperTestDistance = cooperTestDistance
        self.navetteTestLevel = navetteTestLevel
        self.restingHeartRate = restingHeartRate
        self.postExerciseHeartRate = postExerciseHeartRate
        db.session.commit()

    def __repr__(self):
        return f"<InitialAssessment {self.id} - Participant {self.participant_id}>"
