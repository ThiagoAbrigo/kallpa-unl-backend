from app import db

class Program(db.Model):
    __tablename__ = "program"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    schedules = db.relationship('Schedule', backref='program', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Program {self.name}>"
