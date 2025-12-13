from app import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    class Status:
        PRESENT = "present"
        ABSENT = "absent"

