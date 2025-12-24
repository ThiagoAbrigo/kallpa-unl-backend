from app.services import assessment_service

class AssessmentController:

    def get_assessment(self):
        return assessment_service.get_all_assessments()

    def register(self, data):
        return assessment_service.register_evaluation(data)

    def update(self, external_id, data):
        return assessment_service.update_assessment(external_id, data)
