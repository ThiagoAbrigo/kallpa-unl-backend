from flask import Blueprint, request, jsonify
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)
controller = AuthController()

def response_handler(result):
    status_code = result.get("code", 200)
    return jsonify(result), status_code

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    return response_handler(controller.login(data))
