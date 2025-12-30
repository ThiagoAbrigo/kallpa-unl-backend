from flask import Blueprint, jsonify, request
from app.utils.jwt_required import jwt_required
from app.controllers.usercontroller import UserController

user_bp = Blueprint("users", __name__)
controller = UserController()

def response_handler(result):
    print("TYPE:", type(result), result)
    status_code = result.get("code", 200)
    return jsonify(result), status_code

@user_bp.route("/users", methods=["GET"])
def listar_users():
    result = controller.get_users()
    
    if isinstance(result, list):
        return jsonify({"status": "ok", "data": result}), 200
    # ------------------------------------------

    return response_handler(result)

@user_bp.route("/users", methods=["POST"])
def crear_user():
    data = request.json
    return response_handler(controller.create_user(data))


@user_bp.route("/users/initiation", methods=["POST"])
def crear_iniciacion():
    data = request.json
    return response_handler(controller.create_initiation(data))

@user_bp.route("/users/<string:external_id>/status", methods=["PUT"])
def cambiar_estado(external_id):
    data = request.json
    return response_handler(controller.update_status(external_id, data))

@user_bp.route("/users/search", methods=["POST"])
def buscar_usuario():
    data = request.json
    dni = data.get("dni")

    if not dni:
        return jsonify({"status": "error", "msg": "Falta el DNI", "code": 400}), 400

    return response_handler(controller.search_user(dni))
