from flask import Blueprint, request, jsonify
from app.controllers.attendance_controller import AttendanceController

attendance_bp = Blueprint("attendance", __name__)
controller = AttendanceController()


def response_handler(result):
    status_code = result.get("code", 200)
    return jsonify(result), status_code


@attendance_bp.route("/attendance", methods=["POST"])
def registrar_asistencia():
    """Registrar una asistencia individual"""
    data = request.json
    result = controller.registrar_asistencia(data)
    return response_handler(result)


@attendance_bp.route("/attendance/bulk", methods=["POST"])
def registrar_asistencia_masiva():
    """Registrar múltiples asistencias de una sesión"""
    data = request.json
    result = controller.registrar_asistencia_masiva(data)
    return response_handler(result)


@attendance_bp.route("/attendance", methods=["GET"])
def listar_asistencias():
    """Obtener todas las asistencias con filtros opcionales"""
    filters = {
        "participant_external_id": request.args.get("participant_external_id"),
        "schedule_external_id": request.args.get("schedule_external_id"),
        "date": request.args.get("date"),
        "status": request.args.get("status")
    }
    # Remover filtros vacíos
    filters = {k: v for k, v in filters.items() if v}
    result = controller.obtener_asistencias(filters if filters else None)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["GET"])
def obtener_asistencia(external_id):
    """Obtener una asistencia específica por su external_id"""
    result = controller.obtener_asistencia_por_id(external_id)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["PUT"])
def actualizar_asistencia(external_id):
    """Actualizar una asistencia existente"""
    data = request.json
    result = controller.actualizar_asistencia(external_id, data)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["DELETE"])
def eliminar_asistencia(external_id):
    """Eliminar una asistencia"""
    result = controller.eliminar_asistencia(external_id)
    return response_handler(result)


@attendance_bp.route("/attendance/summary/<participant_external_id>", methods=["GET"])
def obtener_resumen(participant_external_id):
    """Obtener resumen de asistencias de un participante"""
    result = controller.obtener_resumen_por_participante(participant_external_id)
    return response_handler(result)
