from app.services import attendance_service


class AttendanceController:

    def registrar_asistencia(self, data):
        """Registrar una asistencia individual"""
        return attendance_service.registrar_asistencia(data)

    def registrar_asistencia_masiva(self, data):
        """Registrar múltiples asistencias de una sesión"""
        return attendance_service.registrar_asistencia_masiva(data)

    def obtener_asistencias(self, filters=None):
        """Obtener todas las asistencias con filtros opcionales"""
        return attendance_service.obtener_asistencias(filters)

    def obtener_asistencia_por_id(self, external_id):
        """Obtener una asistencia específica por su external_id"""
        return attendance_service.obtener_asistencia_por_id(external_id)

    def actualizar_asistencia(self, external_id, data):
        """Actualizar una asistencia existente"""
        return attendance_service.actualizar_asistencia(external_id, data)

    def eliminar_asistencia(self, external_id):
        """Eliminar una asistencia"""
        return attendance_service.eliminar_asistencia(external_id)

    def obtener_resumen_por_participante(self, participant_external_id):
        """Obtener resumen de asistencias de un participante"""
        return attendance_service.obtener_resumen_por_participante(participant_external_id)

    # ========== MÉTODOS PÚBLICOS PARA EL FRONTEND ==========

    def obtener_participantes(self):
        """Obtener todos los participantes"""
        return attendance_service.obtener_participantes()

    def obtener_schedules(self):
        """Obtener todos los horarios"""
        return attendance_service.obtener_schedules()

    def crear_schedule(self, data):
        """Crear un nuevo horario/sesión"""
        return attendance_service.crear_schedule(data)

    def actualizar_schedule(self, schedule_id, data):
        """Actualizar un horario/sesión"""
        return attendance_service.actualizar_schedule(schedule_id, data)

    def eliminar_schedule(self, schedule_id):
        """Eliminar un horario/sesión"""
        return attendance_service.eliminar_schedule(schedule_id)

    def obtener_sesiones_hoy(self):
        """Obtener las sesiones programadas para hoy"""
        return attendance_service.obtener_sesiones_hoy()

    def obtener_historial(self, date_from=None, date_to=None, schedule_id=None):
        """Obtener historial de asistencias"""
        return attendance_service.obtener_historial(date_from, date_to, schedule_id)

    def registrar_asistencia_publica(self, data):
        """Registrar asistencia desde el frontend"""
        return attendance_service.registrar_asistencia_publica(data)

    def obtener_programas(self):
        """Obtener todos los programas"""
        return attendance_service.obtener_programas()

    def obtener_detalle_sesion(self, schedule_id, date):
        """Obtener detalle de asistencia de una sesión"""
        return attendance_service.obtener_detalle_sesion(schedule_id, date)

    def eliminar_asistencia_sesion(self, schedule_id, date):
        """Eliminar asistencia de una sesión"""
        return attendance_service.eliminar_asistencia_sesion(schedule_id, date)
