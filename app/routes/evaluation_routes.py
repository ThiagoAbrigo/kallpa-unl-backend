from flask import Blueprint, request, jsonify
from app.controllers.evaluation_controller import EvaluationController

evaluation_bp = Blueprint("evaluation", __name__)
controller = EvaluationController()


def response_handler(result):
    status_code = result.get("code", 200)
    return jsonify(result), status_code


@evaluation_bp.route("/save-test", methods=["POST"])
def register_evaluation():
    data = request.json
    return response_handler(controller.register(data))

@evaluation_bp.route("/apply_test", methods=["POST"])
def apply_test():
    data = request.json
    return response_handler(controller.apply_test(data))