"""Attendance DAO - Data Access Object for Attendance model"""
from app.dao import BaseDAO
from app.models.attendance import Attendance


class AttendanceDAO(BaseDAO):
    """DAO for Attendance entity"""
    
    def __init__(self):
        super().__init__(Attendance)
    
    def get_by_participant_id(self, participant_id):
        """Get all attendance records for a participant"""
        return Attendance.query.filter_by(participant_id=participant_id).all()
    
    def get_by_participant_and_date(self, participant_id, fecha):
        """Get attendance record by participant and date"""
        return Attendance.query.filter_by(
            participant_id=participant_id,
            fecha=fecha
        ).first()
    
    def get_by_state(self, estado):
        """Get all attendance records with a specific state"""
        return Attendance.query.filter_by(estado=estado).all()
