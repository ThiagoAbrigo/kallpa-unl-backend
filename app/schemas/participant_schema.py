from app.schemas import ma
from app.models.participant import Participant


class ParticipantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Participant
        load_instance = True
        include_fk = True


# Instancias para serializar uno o varios participantes
participant_schema = ParticipantSchema()
participants_schema = ParticipantSchema(many=True)
