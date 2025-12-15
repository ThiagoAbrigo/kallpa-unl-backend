from app import db
from app.models.responsible import Responsible


class ResponsibleDAO:
    """Data Access Object para la entidad Responsible"""

    def get_by_id(self, responsible_id):
        """Obtiene un responsable por su ID"""
        return Responsible.query.get(responsible_id)

    def get_by_participant_id(self, participant_id):
        """Obtiene un responsable por el ID del participante"""
        return Responsible.query.filter_by(participant_id=participant_id).first()

    def create(self, participant_id, nombre, apellido, dni, telefono, parentesco):
        """Crea un nuevo responsable"""
        nuevo = Responsible(
            participant_id=participant_id,
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            telefono=telefono,
            parentesco=parentesco
        )
        db.session.add(nuevo)
        db.session.commit()
        return nuevo

    def update(self, responsible_id, **kwargs):
        """Actualiza un responsable existente"""
        responsable = self.get_by_id(responsible_id)
        if responsable:
            for key, value in kwargs.items():
                if hasattr(responsable, key) and value is not None:
                    setattr(responsable, key, value)
            db.session.commit()
        return responsable

    def delete(self, responsible_id):
        """Elimina un responsable"""
        responsable = self.get_by_id(responsible_id)
        if responsable:
            db.session.delete(responsable)
            db.session.commit()
            return True
        return False
