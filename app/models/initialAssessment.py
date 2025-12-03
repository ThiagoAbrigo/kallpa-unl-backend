from app.models.assessment import Assessment
from app import db

class InitialAssessment(Assessment):
    __tablename__ = 'aerobic_assessment'
    id = db.Column(db.Integer, primary_key=True)
    testCooperDistancia = db.Column(db.Integer)
    testNavetteNivel = db.Column(db.Integer)
    frecuenciaCardiacaReposo = db.Column(db.Integer)
    frecuenciaCardiacaPostEjercicio = db.Column(db.Integer)
    def guardarResultadosAerobicos(self):
        db.session.add(self)
        db.session.commit()
    def editarResultadosAerobicos(self, testCooperDistancia, testNavetteNivel, frecuenciaCardiacaReposo, frecuenciaCardiacaPostEjercicio):
        self.testCooperDistancia = testCooperDistancia
        self.testNavetteNivel = testNavetteNivel
        self.frecuenciaCardiacaReposo = frecuenciaCardiacaReposo
        self.frecuenciaCardiacaPostEjercicio = frecuenciaCardiacaPostEjercicio
        db.session.commit()
    def __repr__(self):
        return f"<AerobicAssessment {self.id} - Participant {self.participant_id}>"
