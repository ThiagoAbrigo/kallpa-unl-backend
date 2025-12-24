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
