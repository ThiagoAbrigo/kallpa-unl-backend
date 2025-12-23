from app.services import evaluation_service

class EvaluationController:

    def register(self, data):
        return evaluation_service.register_test(data)
    
    def apply_test(self, data):
        return evaluation_service.apply_test(data)

