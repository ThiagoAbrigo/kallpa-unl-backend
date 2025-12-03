"""Participant DAO - Data Access Object for Participant model"""
from app.dao import BaseDAO
from app.models.participant import Participante


class ParticipantDAO(BaseDAO):
    """DAO for Participante entity"""
    
    def __init__(self):
        super().__init__(Participante)
    
    def get_by_dni(self, dni):
        """Get participant by DNI"""
        return Participante.query.filter_by(dni=dni).first()
    
    def get_by_email(self, correo):
        """Get participant by email"""
        return Participante.query.filter_by(correo=correo).first()
    
    def get_by_status(self, estado):
        """Get all participants with a specific status"""
        return Participante.query.filter_by(estado=estado).all()
    
    def get_by_type(self, tipo):
        """Get all participants of a specific type"""
        return Participante.query.filter_by(tipo=tipo).all()
