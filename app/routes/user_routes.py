from flask import Blueprint, jsonify
from app.controllers.usercontroller import UserController

user_bp = Blueprint("users", __name__)
controller = UserController()

@user_bp.get("/users")
def listar_users():
    return jsonify(controller.get_users())
