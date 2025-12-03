"""Assessment Schema - Serialization/Deserialization for Assessment model"""
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models.assessment import Assessment


class AssessmentSchema(SQLAlchemyAutoSchema):
    """Schema for Assessment model"""
    
    class Meta:
        model = Assessment
        load_instance = True
        include_relationships = False
    
    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    fecha = fields.Str(required=True)
    peso = fields.Float(required=True)
    talla = fields.Float(required=True)
    imc = fields.Float(dump_only=True)  # Calculated field
    perimetroCintura = fields.Float(required=True)
    envergadura = fields.Float(required=True)


assessment_schema = AssessmentSchema()
assessments_schema = AssessmentSchema(many=True)
