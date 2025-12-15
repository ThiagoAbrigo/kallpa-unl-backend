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
