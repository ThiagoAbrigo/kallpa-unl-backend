from app.models.assessment import Assessment
from app import db

class AerobicAssessment(Assessment):
    __tablename__ = 'aerobic_assessment'
    id = db.Column(db.Integer, primary_key=True)
    testCooperDistancia = db.Column(db.Integer)
    testNavetteNivel = db.Column(db.Integer)
    frecuenciaCardiacaReposo = db.Column(db.Integer)
    frecuenciaCardiacaPostEjercicio = db.Column(db.Integer)
