from app import db
import uuid


class Schedule(db.Model):
    __tablename__ = "schedule"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(
        db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    dayOfWeek = db.Column(db.String(20), nullable=True)  # Null para sesiones específicas
    startTime = db.Column(db.String(10), nullable=False)
    endTime = db.Column(db.String(10), nullable=False)
    maxSlots = db.Column(db.Integer, nullable=False, default=30)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    
    # Nuevos campos para sesiones recurrentes y específicas
    startDate = db.Column(db.String(10), nullable=True)  # Fecha inicio para recurrentes
    endDate = db.Column(db.String(10), nullable=True)    # Fecha fin para recurrentes
    specificDate = db.Column(db.String(10), nullable=True)  # Fecha específica (no recurrente)
    isRecurring = db.Column(db.Boolean, default=True)    # True = recurrente, False = específica
    location = db.Column(db.String(200), nullable=True)  # Ubicación
    description = db.Column(db.String(500), nullable=True)  # Descripción
    
    attendances = db.relationship("Attendance", backref="schedule", lazy=True)

    def __repr__(self):
        return f"<Schedule {self.name}>"
