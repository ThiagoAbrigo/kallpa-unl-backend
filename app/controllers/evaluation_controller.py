from app.services import evaluation_service


class EvaluationController:

    def list(self):
        return evaluation_service.list_tests()

    def register(self, data):
        return evaluation_service.register_test(data)

    def apply_test(self, data):
        return evaluation_service.apply_test(data)

    def history(
        self,
        participant_external_id,
        test_external_id,
        months=6,
    ):
        return evaluation_service.get_history(
            participant_external_id=participant_external_id,
            test_external_id=test_external_id,
            months=months,
        )

    def list_tests_for_participant(self, participant_external_id):
        return evaluation_service.list_tests_for_participant(participant_external_id)
