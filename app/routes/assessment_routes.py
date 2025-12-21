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
