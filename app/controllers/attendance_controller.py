from app.services import attendance_service

class AttendanceController:
    @staticmethod
    def registrar_asistencia(data):
        return attendance_service.registrar_asistencia(data)
