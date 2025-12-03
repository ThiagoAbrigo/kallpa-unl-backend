"""Attendance Schema - Serialization/Deserialization for Attendance model"""
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models.attendance import Attendance


class AttendanceSchema(SQLAlchemyAutoSchema):
    """Schema for Attendance model"""
    
    class Meta:
        model = Attendance
        load_instance = True
        include_relationships = False
    
    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    fecha = fields.Str(required=True)
    estado = fields.Str(required=True)


attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)
