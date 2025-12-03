"""Assessment DAO - Data Access Object for Assessment model"""
from app.dao import BaseDAO
from app.models.assessment import Assessment


class AssessmentDAO(BaseDAO):
    """DAO for Assessment entity"""
    
    def __init__(self):
        super().__init__(Assessment)
    
    def get_by_participant_id(self, participant_id):
        """Get all assessments for a participant"""
        return Assessment.query.filter_by(participant_id=participant_id).all()
    
    def get_by_participant_and_date(self, participant_id, fecha):
        """Get assessment record by participant and date"""
        return Assessment.query.filter_by(
            participant_id=participant_id,
            fecha=fecha
        ).first()
    
    def get_latest_by_participant(self, participant_id):
        """Get the latest assessment for a participant"""
        return Assessment.query.filter_by(
            participant_id=participant_id
        ).order_by(Assessment.fecha.desc()).first()
