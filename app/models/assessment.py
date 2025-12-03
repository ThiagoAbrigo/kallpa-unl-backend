from app import db
class Assessment(db.Model):
    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participante.id'), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    talla = db.Column(db.Float, nullable=False)
    imc = db.Column(db.Float, nullable=False)
    perimetroCintura = db.Column(db.Float, nullable=False)
    envergadura = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'assessment',
        'polymorphic_on': type
    }

    def calcularIMC(self):
        if self.talla > 0:
            self.imc = self.peso / (self.talla ** 2)
        else:
            self.imc = 0

    def guardarResultados(self):
        db.session.add(self)
        db.session.commit()

    def editarResultados(self, fecha, peso, talla, perimetroCintura, envergadura):
        self.fecha = fecha
        self.peso = peso
        self.talla = talla
        self.perimetroCintura = perimetroCintura
        self.envergadura = envergadura
        self.calcularIMC()
        db.session.commit()