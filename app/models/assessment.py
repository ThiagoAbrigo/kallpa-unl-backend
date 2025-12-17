from app import db

class Assessment(db.Model):
    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    waistPerimeter = db.Column(db.Float, nullable=False)
    wingspan = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'assessment',
        'polymorphic_on': type
    }

    def calculateBMI(self):
        if self.height > 0:
            self.bmi = self.weight / (self.height ** 2)
        else:
            self.bmi = 0

    def saveResults(self):
        db.session.add(self)
        db.session.commit()

    def editResults(self, date, weight, height, waistPerimeter, wingspan):
        self.date = date
        self.weight = weight
        self.height = height
        self.waistPerimeter = waistPerimeter
        self.wingspan = wingspan
        self.calculateBMI()
        db.session.commit()
