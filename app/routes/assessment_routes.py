from flask import Blueprint, request, jsonify
from app.controllers.assessment_controller import AssessmentController

assessment_bp = Blueprint("assessment", __name__)
controller = AssessmentController()


def response_handler(result):
    status_code = result.get("code", 200)
    return jsonify(result), status_code


@assessment_bp.route("/save-assessment", methods=["POST"])
def register_evaluation():
    data = request.json
    return response_handler(controller.register(data))


@assessment_bp.route("/list-assessment", methods=["GET"])
def list_evaluation():
    return response_handler(controller.get_assessment())


@assessment_bp.route("/update-assessment/<string:external_id>", methods=["PUT"])
def update_evaluation(external_id):
    data = request.json
    return response_handler(controller.update(external_id, data))


@assessment_bp.route(
    "/participants/<string:participant_external_id>/assessments", methods=["GET"]
)
def search_evaluation(participant_external_id):
    return response_handler(
        controller.get_participants_external_id(participant_external_id)
    )


@assessment_bp.route("/assessments/history", methods=["GET"])
def anthropometric_history_general():
    months_param = request.args.get("months", default=3, type=int)

    if months_param not in [3, 6]:
        months_param = 3

    return response_handler(
        controller.get_anthropometric_history(months_param)
    )

@assessment_bp.route("/average-bmi", methods=["GET"])
def average_bmi():
    return response_handler(controller.get_average_bmi())
