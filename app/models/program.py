from app import db
import uuid


class Program(db.Model):
    __tablename__ = "program"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(
        db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    schedules = db.relationship(
        "Schedule", backref="program", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Program {self.name}>"
