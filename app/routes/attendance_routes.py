from flask import Blueprint, request, jsonify
from app.controllers.attendance_controller import AttendanceController

attendance_bp = Blueprint("attendance", __name__)
controller = AttendanceController()

@attendance_bp.route("/attendance", methods=["POST"])
def registrar_asistencia():
    data = request.json
    result = controller.registrar_asistencia(data)

    if result["status"] == "error":
        return jsonify(result), 400

    return jsonify(result), 200

@attendance_bp.route("/attendance", methods=["GET"])
def listar_asistencias():
    registros = controller.listar()
    return jsonify(registros)
