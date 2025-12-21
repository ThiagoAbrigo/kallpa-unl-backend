from flask import Blueprint, request, jsonify
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)
controller = AuthController()


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    response, status_code = controller.login(data)
    return jsonify(response), status_code
