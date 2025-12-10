#This class Program has two values the id and name and relates 1 to * with schedule, but schedule is a composition of program meaning that schedule contains program

from app import db

class Program(db.Model):
    __tablename__ = "program"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    schedules = db.relationship('Schedule', backref='program', lazy=True, cascade= "all, delete-orphan")
    def __repr__(self):
        return f"<Program {self.name}>"
    
                               
                               