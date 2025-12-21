import uuid
from app import db

class Assessment(db.Model):
    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(
        db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    participant_id = db.Column(
        db.Integer, db.ForeignKey("participant.id"), nullable=False
    )
    date = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    waistPerimeter = db.Column(db.Float, nullable=False)
    wingspan = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50))

    __mapper_args__ = {"polymorphic_identity": "assessment", "polymorphic_on": type}

    def saveResults(self):
        db.session.add(self)
        db.session.commit()
