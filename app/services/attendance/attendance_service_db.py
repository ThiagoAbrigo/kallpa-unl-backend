"""Attendance Service DB - Business logic for attendance using DAO pattern"""
from app.dao.attendance_dao import AttendanceDAO
from app.schemas.attendance_schema import attendance_schema, attendances_schema


class AttendanceServiceDB:
    """Service for attendance operations using database"""
    
    def __init__(self):
        self.attendance_dao = AttendanceDAO()
    
    def registrar_asistencia(self, data):
        """Register a new attendance record"""
        try:
            # Validate required fields
            if not all(k in data for k in ["participant_id", "fecha", "estado"]):
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": "Campos requeridos: participant_id, fecha, estado"
                }
            
            # Create attendance using DAO
            attendance = self.attendance_dao.create(
                participant_id=data["participant_id"],
                fecha=data["fecha"],
                estado=data["estado"]
            )
            
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Asistencia registrada en BD",
                "data": attendance_schema.dump(attendance)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error al registrar asistencia: {str(e)}"
            }
    
    def obtener_asistencias_por_participante(self, participant_id):
        """Get all attendance records for a participant"""
        try:
            attendances = self.attendance_dao.get_by_participant_id(participant_id)
            return {
                "status": "ok",
                "origen": "db",
                "msg": f"Se encontraron {len(attendances)} registros",
                "data": attendances_schema.dump(attendances)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error al obtener asistencias: {str(e)}"
            }
    
    def obtener_asistencia_por_fecha(self, participant_id, fecha):
        """Get attendance record for a participant on specific date"""
        try:
            attendance = self.attendance_dao.get_by_participant_and_date(participant_id, fecha)
            if not attendance:
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": "No se encontró registro de asistencia"
                }
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Registro encontrado",
                "data": attendance_schema.dump(attendance)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error: {str(e)}"
            }
    
    def editar_asistencia(self, attendance_id, data):
        """Edit an attendance record"""
        try:
            attendance = self.attendance_dao.update(attendance_id, **data)
            if not attendance:
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": "Registro no encontrado"
                }
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Asistencia actualizada",
                "data": attendance_schema.dump(attendance)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error al actualizar: {str(e)}"
            }
    
    def eliminar_asistencia(self, attendance_id):
        """Delete an attendance record"""
        try:
            deleted = self.attendance_dao.delete(attendance_id)
            if not deleted:
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": "Registro no encontrado"
                }
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Asistencia eliminada"
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error al eliminar: {str(e)}"
            }

