"""Participant Schema - Serialization/Deserialization for Participant model"""
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models.participant import Participante


class ParticipantSchema(SQLAlchemyAutoSchema):
    """Schema for Participante model"""
    
    class Meta:
        model = Participante
        load_instance = True
        include_relationships = False
    
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    apellido = fields.Str(required=True)
    edad = fields.Int(required=True)
    dni = fields.Str(required=True)
    telefono = fields.Str(required=True)
    correo = fields.Email(required=True)
    direccion = fields.Str(required=True)
    estado = fields.Str(required=True)
    tipo = fields.Str(required=True)


participant_schema = ParticipantSchema()
participants_schema = ParticipantSchema(many=True)
