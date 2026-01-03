from app.services import attendance_service


class AttendanceController:

    def register_attendance(self, data):
        """Registrar una asistencia individual"""
        return attendance_service.register_attendance(data)

    def register_bulk_attendance(self, data):
        """Registrar múltiples asistencias de una sesión"""
        return attendance_service.register_bulk_attendance(data)

    def get_attendances(self, filters=None):
        """Obtener todas las asistencias con filtros opcionales"""
        return attendance_service.get_attendances(filters)

    def get_attendance_by_id(self, external_id):
        """Obtener una asistencia específica por su external_id"""
        return attendance_service.get_attendance_by_id(external_id)

    def update_attendance(self, external_id, data):
        """Actualizar una asistencia existente"""
        return attendance_service.update_attendance(external_id, data)

    def delete_attendance(self, external_id):
        """Eliminar una asistencia"""
        return attendance_service.delete_attendance(external_id)

    def get_participant_summary(self, participant_external_id):
        """Obtener resumen de asistencias de un participante"""
        return attendance_service.get_participant_summary(participant_external_id)

    # ========== MÉTODOS PÚBLICOS PARA EL FRONTEND ==========

    def get_participants(self):
        """Obtener todos los participantes"""
        return attendance_service.get_participants()

    def get_schedules(self):
        """Obtener todos los horarios"""
        return attendance_service.get_schedules()

    def create_schedule(self, data):
        """Crear un nuevo horario/sesión"""
        return attendance_service.create_schedule(data)

    def update_schedule(self, schedule_id, data):
        """Actualizar un horario/sesión"""
        return attendance_service.update_schedule(schedule_id, data)

    def delete_schedule(self, schedule_id):
        """Eliminar un horario/sesión"""
        return attendance_service.delete_schedule(schedule_id)

    def get_today_sessions(self):
        """Obtener las sesiones programadas para hoy"""
        return attendance_service.get_today_sessions()

    def get_history(self, date_from=None, date_to=None, schedule_id=None, day_filter=None):
        """Obtener historial de asistencias"""
        return attendance_service.get_history(date_from, date_to, schedule_id, day_filter)

    def register_public_attendance(self, data):
        """Registrar asistencia desde el frontend"""
        return attendance_service.register_public_attendance(data)

    def get_programs(self):
        """Obtener todos los programas"""
        return attendance_service.get_programs()

    def get_session_detail(self, schedule_id, date):
        """Obtener detalle de asistencia de una sesión"""
        return attendance_service.get_session_detail(schedule_id, date)

    def delete_session_attendance(self, schedule_id, date):
        """Eliminar asistencia de una sesión"""
        return attendance_service.delete_session_attendance(schedule_id, date)
