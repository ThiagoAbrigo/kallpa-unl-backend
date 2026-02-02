from flask import Blueprint, request, jsonify
from app.controllers.attendance_controller import AttendanceController
from app.utils.jwt_required import jwt_required

# Rutas del módulo de Gestión de Asistencias - Proyecto Kallpa UNL
# Incluye endpoints para: registros, horarios, sesiones y estadísticas

attendance_bp = Blueprint("attendance", __name__)
controller = AttendanceController()


def response_handler(result):
    status_code = result.get("code", 200)
    return jsonify(result), status_code


# === CRUD BÁSICO DE ASISTENCIAS ===

@attendance_bp.route("/attendance", methods=["POST"])
@jwt_required
def register_attendance():
    # Registro individual de asistencia
    data = request.json
    result = controller.register_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance/bulk", methods=["POST"])
@jwt_required
def register_bulk_attendance():
    # Registro masivo para una sesión completa
    data = request.json
    result = controller.register_bulk_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance", methods=["GET"])
@jwt_required
def list_attendances():
    # Consulta con filtros: participante, horario, fecha, estado
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
@jwt_required
def get_attendance(external_id):
    # Búsqueda por ID externo
    result = controller.get_attendance_by_id(external_id)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["PUT"])
@jwt_required
def update_attendance(external_id):
    # Modificación de estado presente/ausente
    data = request.json
    result = controller.update_attendance(external_id, data)
    return response_handler(result)


@attendance_bp.route("/attendance/<external_id>", methods=["DELETE"])
@jwt_required
def delete_attendance(external_id):
    # Eliminación física de registro
    result = controller.delete_attendance(external_id)
    return response_handler(result)


@attendance_bp.route("/attendance/summary/<participant_external_id>", methods=["GET"])
@jwt_required
def get_summary(participant_external_id):
    # Estadísticas: total, presentes, ausentes, porcentaje
    result = controller.get_participant_summary(participant_external_id)
    return response_handler(result)


# === ENDPOINTS PÚBLICOS PARA DASHBOARD ===

@attendance_bp.route("/attendance/v2/public/participants", methods=["GET"])
def get_participants():
    # Lista participantes con porcentajes calculados
    program = request.args.get("program")
    result = controller.get_participants(program)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules", methods=["GET"])
def get_schedules():
    # Lista horarios/sesiones activas
    result = controller.get_schedules()
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules", methods=["POST"])
@jwt_required
def create_schedule():
    # Creación con validaciones de solapamiento
    data = request.json
    result = controller.create_schedule(data)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules/<schedule_id>", methods=["PUT"])
@jwt_required
def update_schedule(schedule_id):
    # Modificación de horarios existentes
    data = request.json
    result = controller.update_schedule(schedule_id, data)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/schedules/<schedule_id>", methods=["DELETE"])
@jwt_required
def delete_schedule(schedule_id):
    # Eliminación lógica (marca como inactivo)
    result = controller.delete_schedule(schedule_id)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/sessions/today", methods=["GET"])
@jwt_required
def get_today_sessions():
    # Sesiones del día: recurrentes + fechas específicas
    result = controller.get_today_sessions()
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/history", methods=["GET"])
@jwt_required
def get_history():
    # Historial con filtros de rango de fechas y sesión
    date_from = request.args.get("date_from") or request.args.get("startDate")
    date_to = request.args.get("date_to") or request.args.get("endDate")
    schedule_id = request.args.get("schedule_id") or request.args.get("scheduleId")
    day_filter = request.args.get("day")
    
    result = controller.get_history(date_from, date_to, schedule_id, day_filter)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/register", methods=["POST"])
@jwt_required
def register_public_attendance():
    # Endpoint principal para registro desde dashboard
    data = request.json
    result = controller.register_public_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/programs", methods=["GET"])
@jwt_required
def get_programs():
    # Lista de programas disponibles (FUNCIONAL, INICIACION)
    result = controller.get_programs()
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/history/session/<schedule_id>/<date>", methods=["GET"])
@jwt_required
def get_session_detail(schedule_id, date):
    # Detalle completo de participantes en una sesión específica
    result = controller.get_session_detail(schedule_id, date)
    return response_handler(result)


@attendance_bp.route("/attendance/v2/public/history/session/<schedule_id>/<date>", methods=["DELETE"])
@jwt_required
def delete_session_attendance(schedule_id, date):
    # Eliminar todos los registros de una fecha
    result = controller.delete_session_attendance(schedule_id, date)
    return response_handler(result)


# === RUTAS SIMPLIFICADAS (ALTERNATIVAS) ===

@attendance_bp.route("/attendance/participants", methods=["GET"])
@jwt_required
def get_participants_simple():
    # Versión corta de ruta de participantes
    result = controller.get_participants()
    return response_handler(result)


@attendance_bp.route("/attendance/schedules", methods=["GET"])
@jwt_required
def get_schedules_simple():
    # Versión corta de horarios
    result = controller.get_schedules()
    return response_handler(result)


@attendance_bp.route("/attendance/schedules", methods=["POST"])
@jwt_required
def create_schedule_simple():
    # Versión corta de creación
    data = request.json
    result = controller.create_schedule(data)
    return response_handler(result)


@attendance_bp.route("/attendance/schedules/<schedule_id>", methods=["PUT"])
@jwt_required
def update_schedule_simple(schedule_id):
    # Versión corta de actualización
    data = request.json
    result = controller.update_schedule(schedule_id, data)
    return response_handler(result)


@attendance_bp.route("/attendance/schedules/<schedule_id>", methods=["DELETE"])
@jwt_required
def delete_schedule_simple(schedule_id):
    # Versión corta de eliminación
    result = controller.delete_schedule(schedule_id)
    return response_handler(result)


# === COMPATIBILIDAD CON FRONTEND LEGACY ===

@attendance_bp.route("/attendance/sessions/today", methods=["GET"])
@jwt_required
def get_today_sessions_legacy():
    result = controller.get_today_sessions()
    return response_handler(result)


@attendance_bp.route("/attendance/register", methods=["POST"])
@jwt_required
def register_attendance_simple():
    # Registro masivo sin prefijo v2
    data = request.json
    result = controller.register_public_attendance(data)
    return response_handler(result)


@attendance_bp.route("/attendance/history", methods=["GET"])
@jwt_required
def get_history_simple():
    # Historial sin prefijo v2
    start_date = request.args.get("startDate") or request.args.get("date_from")
    end_date = request.args.get("endDate") or request.args.get("date_to")
    schedule_id = request.args.get("scheduleId")
    day_filter = request.args.get("day")
    result = controller.get_history(start_date, end_date, schedule_id, day_filter)
    return response_handler(result)


@attendance_bp.route("/attendance/session/<schedule_id>/<date>", methods=["GET"])
@jwt_required
def get_session_detail_legacy(schedule_id, date):
    # Detalle de sesión sin prefijo v2
    result = controller.get_session_detail(schedule_id, date)
    return response_handler(result)


@attendance_bp.route("/attendance/session/<schedule_id>/<date>", methods=["DELETE"])
@jwt_required
def delete_session_attendance_legacy(schedule_id, date):
    # Eliminación de sesión sin prefijo v2
    result = controller.delete_session_attendance(schedule_id, date)
    return response_handler(result)

@attendance_bp.route("/attendance/daily/", defaults={"date": None}, methods=["GET"])

@attendance_bp.route("/attendance/daily/<date>", methods=["GET"])

def get_daily_attendance(date=None):
    # Análisis diario: sesión con menor porcentaje de asistencia
    result = controller.get_daily_attendance_percentage(date)
    return response_handler(result)