from flask import Blueprint, request, jsonify
from app.controllers.attendance_controller import AttendanceController

attendance_bp = Blueprint("attendance", __name__)
controller = AttendanceController()


def response_handler(result):
    status_code = result.get("code", 200)
    return jsonify(result), status_code


# ========== ATTENDANCE MANAGEMENT ==========

@attendance_bp.route("/attendance", methods=["POST"])
def register_attendance():
    """Registrar una asistencia individual"""
    data = request.json
    result = controller.register_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance/bulk", methods=["POST"])
def register_bulk_attendance():
    """Registrar múltiples asistencias de una sesión"""
    data = request.json
    result = controller.register_bulk_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance", methods=["GET"])
def list_attendances():
    """Obtener todas las asistencias con filtros opcionales"""
    filters = {
        "participant_external_id": request.args.get("participant_external_id"),
        "schedule_external_id": request.args.get("schedule_external_id"),
        "date": request.args.get("date"),
        "status": request.args.get("status")
    }
    filters = {k: v for k, v in filters.items() if v}
    result = controller.get_attendances(filters if filters else None)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["GET"])
def get_attendance(external_id):
    """Obtener una asistencia específica por su external_id"""
    result = controller.get_attendance_by_id(external_id)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["PUT"])
def update_attendance(external_id):
    """Actualizar una asistencia existente"""
    data = request.json
    result = controller.update_attendance(external_id, data)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["DELETE"])
def delete_attendance(external_id):
    """Eliminar una asistencia"""
    result = controller.delete_attendance(external_id)
    return response_handler(result)


@attendance_bp.route("/attendance/summary/<participant_external_id>", methods=["GET"])
def get_summary(participant_external_id):
    """Obtener resumen de asistencias de un participante"""
    result = controller.get_participant_summary(participant_external_id)
    return response_handler(result)


# ========== PUBLIC / FRONTEND ROUTES ==========

@attendance_bp.route("/attendance/v2/public/participants", methods=["GET"])
def get_participants():
    """Obtener todos los participantes"""
    program = request.args.get("program")
    result = controller.get_participants(program)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules", methods=["GET"])
def get_schedules():
    """Obtener todos los horarios"""
    result = controller.get_schedules()
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules", methods=["POST"])
def create_schedule():
    """Crear un nuevo horario/sesión"""
    data = request.json
    result = controller.create_schedule(data)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules/<schedule_id>", methods=["PUT"])
def update_schedule(schedule_id):
    """Actualizar un horario/sesión"""
    data = request.json
    result = controller.update_schedule(schedule_id, data)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules/<schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    """Eliminar un horario/sesión"""
    result = controller.delete_schedule(schedule_id)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/sessions/today", methods=["GET"])
def get_today_sessions():
    """Obtener las sesiones programadas para hoy"""
    result = controller.get_today_sessions()
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/history", methods=["GET"])
def get_history():
    """Obtener historial de asistencias con filtros opcionales"""
    date_from = request.args.get("date_from") or request.args.get("startDate")
    date_to = request.args.get("date_to") or request.args.get("endDate")
    schedule_id = request.args.get("schedule_id") or request.args.get("scheduleId")
    day_filter = request.args.get("day")
    
    result = controller.get_history(date_from, date_to, schedule_id, day_filter)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/register", methods=["POST"])
def register_public_attendance():
    """Registrar asistencia desde el frontend"""
    data = request.json
    result = controller.register_public_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/programs", methods=["GET"])
def get_programs():
    """Obtener todos los programas"""
    result = controller.get_programs()
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/history/session/<schedule_id>/<date>", methods=["GET"])
def get_session_detail(schedule_id, date):
    """Obtener detalle de asistencia de una sesión específica"""
    result = controller.get_session_detail(schedule_id, date)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/history/session/<schedule_id>/<date>", methods=["DELETE"])
def delete_session_attendance(schedule_id, date):
    """Eliminar asistencia de una sesión específica"""
    result = controller.delete_session_attendance(schedule_id, date)
    return response_handler(result)


# ========== RUTAS SIMPLIFICADAS PARA EL NUEVO FRONTEND ==========

@attendance_bp.route("/attendance/participants", methods=["GET"])
def get_participants_simple():
    """Obtener todos los participantes (ruta simplificada)"""
    result = controller.get_participants()
    return response_handler(result)


@attendance_bp.route("/attendance/schedules", methods=["GET"])
def get_schedules_simple():
    """Obtener todos los horarios (ruta simplificada)"""
    result = controller.get_schedules()
    return response_handler(result)


@attendance_bp.route("/attendance/schedules", methods=["POST"])
def create_schedule_simple():
    """Crear un nuevo horario (ruta simplificada)"""
    data = request.json
    result = controller.create_schedule(data)
    return response_handler(result)


@attendance_bp.route("/attendance/schedules/<schedule_id>", methods=["PUT"])
def update_schedule_simple(schedule_id):
    """Actualizar un horario (ruta simplificada)"""
    data = request.json
    result = controller.update_schedule(schedule_id, data)
    return response_handler(result)


@attendance_bp.route("/attendance/schedules/<schedule_id>", methods=["DELETE"])
def delete_schedule_simple(schedule_id):
    """Eliminar un horario (ruta simplificada)"""
    result = controller.delete_schedule(schedule_id)
    return response_handler(result)


# ========== RUTAS LEGACY (Compatibilidad Frontend) ==========

@attendance_bp.route("/attendance/sessions/today", methods=["GET"])
def get_today_sessions_legacy():
    result = controller.get_today_sessions()
    return response_handler(result)


@attendance_bp.route("/attendance/register", methods=["POST"])
def register_attendance_simple():
    """Registrar asistencia masiva (ruta simplificada)"""
    data = request.json
    result = controller.register_public_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance/history", methods=["GET"])
def get_history_simple():
    """Obtener historial de asistencias (ruta simplificada)"""
    start_date = request.args.get("startDate") or request.args.get("date_from")
    end_date = request.args.get("endDate") or request.args.get("date_to")
    schedule_id = request.args.get("scheduleId")
    day_filter = request.args.get("day")
    result = controller.get_history(start_date, end_date, schedule_id, day_filter)
    return response_handler(result)


@attendance_bp.route("/attendance/session/<schedule_id>/<date>", methods=["GET"])
def get_session_detail_legacy(schedule_id, date):
    """Obtener detalle de una sesión específica (ruta legacy)"""
    result = controller.get_session_detail(schedule_id, date)
    return response_handler(result)


@attendance_bp.route("/attendance/session/<schedule_id>/<date>", methods=["DELETE"])
def delete_session_attendance_legacy(schedule_id, date):
    """Eliminar registro de asistencia de una fecha (ruta legacy)"""
    result = controller.delete_session_attendance(schedule_id, date)
    return response_handler(result)


@attendance_bp.route("/attendance/today/average", methods=["GET"])
def get_today_attendance_average():
    """Obtener el promedio de asistencia de todos los participantes en el día actual."""
    average = controller.get_today_attendance_average()
    return response_handler(average)
