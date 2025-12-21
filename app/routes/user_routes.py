from flask import Blueprint, jsonify, request
from app.controllers.usercontroller import UserController

user_bp = Blueprint("users", __name__)
controller = UserController()


@user_bp.route("/users", methods=["GET"])
def listar_users():
    return jsonify(controller.get_users())


@user_bp.route("/users", methods=["POST"])
def crear_user():
    data = request.json
    response, status = controller.create_user(data)
    return jsonify(response), status


@user_bp.route("/users/initiation", methods=["POST"])
def crear_iniciacion():
    data = request.json
    response, status = controller.create_initiation(data)
    return jsonify(response), status


@user_bp.route("/users/<string:external_id>/status", methods=["PUT"])
def cambiar_estado(external_id):
    data = request.json
    response, status = controller.update_status(external_id, data)
    return jsonify(response), status


# ✅ SEGURO (El DNI va encriptado/oculto en el cuerpo del mensaje)
@user_bp.route("/users/search", methods=["POST"])
def buscar_usuario():
    data = request.json
    dni = data.get('dni')  # Extraemos el DNI del JSON
    
    if not dni:
        return jsonify({"status": "error", "msg": "Falta el DNI"}), 400

    response, status = controller.search_user(dni)
    return jsonify(response), status
