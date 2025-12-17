from app import db

class Schedule(db.Model):
    __tablename__ = "schedule"

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dayOfWeek = db.Column(db.String(20), nullable=False)
    startTime = db.Column(db.String(10), nullable=False)
    endTime = db.Column(db.String(10), nullable=False)
    maxSlots = db.Column(db.Integer, nullable=False)
    attendances = db.relationship('Attendance', backref='schedule', lazy=True)

    def __repr__(self):
        return f"<Schedule {self.name}>"
