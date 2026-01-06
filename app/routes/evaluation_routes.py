from flask import Blueprint, request, jsonify
from app.controllers.evaluation_controller import EvaluationController
from app.utils.roles_required import roles_required
from app.utils.jwt_required import jwt_required

evaluation_bp = Blueprint("evaluation", __name__)
controller = EvaluationController()


def response_handler(result):
    status_code = result.get("code", 200)
    return jsonify(result), status_code


@evaluation_bp.route("/list-test", methods=["GET"])
@jwt_required
def list_test():
    return response_handler(controller.list())


@evaluation_bp.route("/save-test", methods=["POST"])
# @roles_required("DOCENTE")
def register_evaluation():
    data = request.json
    return response_handler(controller.register(data))


@evaluation_bp.route("/apply_test", methods=["POST"])
@roles_required("DOCENTE", "PASANTE")
def apply_test():
    data = request.json
    return response_handler(controller.apply_test(data))


# @evaluation_bp.route("/history", methods=["GET"])
# def history():
#     participant_external_id = request.args.get("participant_external_id")
#     test_external_id = request.args.get("test_external_id")

#     try:
#         months = int(request.args.get("months", 6))
#     except (ValueError, TypeError):
#         months = 6

#     return response_handler(
#         controller.history(
#             participant_external_id=participant_external_id,
#             test_external_id=test_external_id,
#             months=months,
#         )
#     )

@evaluation_bp.route("/history", methods=["GET"])
def history():
    participant_external_id = request.args.get("participant_external_id")
    test_external_id = request.args.get("test_external_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    return response_handler(
        controller.history(
            participant_external_id=participant_external_id,
            test_external_id=test_external_id,
            start_date=start_date,
            end_date=end_date,
        )
    )


@evaluation_bp.route("/list-tests-participant", methods=["GET"])
def list_tests_for_participant_endpoint():
    participant_external_id = request.args.get("participant_external_id")
    return response_handler(
        controller.list_tests_for_participant(participant_external_id)
    )
