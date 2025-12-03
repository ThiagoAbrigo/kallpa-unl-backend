#Esta clase periodicTest hereda de la clase assessment y tiene estos atributos la clase de periodicTest burpees int sentadiilas int saltoVertical int plancha int dominadas int , hazlo en ingles
from app.models.assessment import Assessment
from app import db

class PeriodicTest(Assessment):
    __tablename__ = "periodicTest"

    id = db.Column(db.Integer, primary_key=True)
    burpees = db.Column(db.Integer, nullable=False)
    sentadillas = db.Column(db.Integer, nullable=False)
    saltoVertical = db.Column(db.Integer, nullable=False)
    plancha = db.Column(db.Integer, nullable=False)
    dominadas = db.Column(db.Integer, nullable=False)