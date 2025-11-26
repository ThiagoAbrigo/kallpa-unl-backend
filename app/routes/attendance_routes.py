from flask import Blueprint, request, jsonify
from app.controllers.attendance_controller import AttendanceController

attendance_bp = Blueprint("attendance", __name__)
controller = AttendanceController()

@attendance_bp.route("/attendance", methods=["POST"])
def registrar_asistencia():
    data = request.json
    result = controller.registrar_asistencia(data)
    return jsonify(result), 201

@attendance_bp.route("/attendance", methods=["GET"])
def listar_asistencias():
    registros = controller.listar()
    return jsonify(registros)
