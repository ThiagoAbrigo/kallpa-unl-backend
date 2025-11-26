from app.models.attendance import Attendance
from app import db

class AttendanceServiceDB:
    def registrar_asistencia(self, data):
        nuevo = Attendance(
            usuario_id=data["user_id"],
            fecha=data["fecha"],
            estado=data["estado"]
        )
        db.session.add(nuevo)
        db.session.commit()

        return {
            "status": "ok",
            "origen": "db",
            "msg": "Asistencia registrada en BD",
            "data": {
                "id": nuevo.id,
                "usuario_id": nuevo.usuario_id,
                "fecha": nuevo.fecha,
                "estado": nuevo.estado
            }
        }
