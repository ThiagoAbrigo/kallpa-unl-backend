from app.services import assessment_service

class AssessmentController:
    def register(self, data):
        return assessment_service.register_evaluation(data)
