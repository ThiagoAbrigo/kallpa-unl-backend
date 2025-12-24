from app.models.attendance import Attendance
from app.models.participant import Participant
from app.models.schedule import Schedule
from app.utils.responses import success_response, error_response
from app import db
from datetime import date


class AttendanceServiceDB:

    def registrar_asistencia(self, data):
        """Registrar una asistencia individual"""
        try:
            # Validar campos requeridos
            campos = ["participant_external_id", "schedule_external_id", "status"]
            for campo in campos:
                if campo not in data:
                    return error_response(f"Falta el campo requerido: {campo}")

            # Validar status
            valid_statuses = [Attendance.Status.PRESENT, Attendance.Status.ABSENT]
            if data["status"] not in valid_statuses:
                return error_response(f"Estado inválido. Use: {valid_statuses}")

            # Buscar participant por external_id
            participant = Participant.query.filter_by(external_id=data["participant_external_id"]).first()
            if not participant:
                return error_response("Participante no encontrado", code=404)

            # Buscar schedule por external_id
            schedule = Schedule.query.filter_by(external_id=data["schedule_external_id"]).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            nuevo = Attendance(
                participant_id=participant.id,
                schedule_id=schedule.id,
                date=data.get("date", date.today().isoformat()),
                status=data["status"]
            )
            db.session.add(nuevo)
            db.session.commit()

            return success_response(
                msg="Asistencia registrada en BD",
                data={
                    "external_id": nuevo.external_id,
                    "participant_external_id": data["participant_external_id"],
                    "schedule_external_id": data["schedule_external_id"],
                    "date": nuevo.date,
                    "status": nuevo.status
                }
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def registrar_asistencia_masiva(self, data):
        """Registrar múltiples asistencias de una sesión"""
        try:
            if "schedule_external_id" not in data:
                return error_response("Falta el campo: schedule_external_id")
            
            if "attendances" not in data or not isinstance(data["attendances"], list):
                return error_response("Falta el campo: attendances (debe ser una lista)")

            # Buscar schedule
            schedule = Schedule.query.filter_by(external_id=data["schedule_external_id"]).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            fecha = data.get("date", date.today().isoformat())
            registros_creados = []

            for item in data["attendances"]:
                if "participant_external_id" not in item or "status" not in item:
                    continue

                participant = Participant.query.filter_by(external_id=item["participant_external_id"]).first()
                if not participant:
                    continue

                nuevo = Attendance(
                    participant_id=participant.id,
                    schedule_id=schedule.id,
                    date=fecha,
                    status=item["status"]
                )
                db.session.add(nuevo)
                registros_creados.append({
                    "participant_external_id": item["participant_external_id"],
                    "status": item["status"]
                })

            db.session.commit()

            return success_response(
                msg=f"Se registraron {len(registros_creados)} asistencias en BD",
                data={"total": len(registros_creados), "attendances": registros_creados}
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def obtener_asistencias(self, filters=None):
        """Obtener todas las asistencias con filtros opcionales"""
        try:
            query = Attendance.query

            if filters:
                if filters.get("participant_external_id"):
                    participant = Participant.query.filter_by(external_id=filters["participant_external_id"]).first()
                    if participant:
                        query = query.filter_by(participant_id=participant.id)
                if filters.get("schedule_external_id"):
                    schedule = Schedule.query.filter_by(external_id=filters["schedule_external_id"]).first()
                    if schedule:
                        query = query.filter_by(schedule_id=schedule.id)
                if filters.get("date"):
                    query = query.filter_by(date=filters["date"])
                if filters.get("status"):
                    query = query.filter_by(status=filters["status"])

            attendances = query.all()
            result = []
            for a in attendances:
                result.append({
                    "external_id": a.external_id,
                    "participant_external_id": a.participant.external_id,
                    "schedule_external_id": a.schedule.external_id,
                    "date": a.date,
                    "status": a.status
                })

            return success_response(
                msg="Asistencias obtenidas correctamente",
                data=result
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def obtener_asistencia_por_id(self, external_id):
        """Obtener una asistencia específica por su external_id"""
        try:
            attendance = Attendance.query.filter_by(external_id=external_id).first()

            if not attendance:
                return error_response("Asistencia no encontrada", code=404)

            return success_response(
                msg="Asistencia encontrada",
                data={
                    "external_id": attendance.external_id,
                    "participant_external_id": attendance.participant.external_id,
                    "schedule_external_id": attendance.schedule.external_id,
                    "date": attendance.date,
                    "status": attendance.status
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def actualizar_asistencia(self, external_id, data):
        """Actualizar una asistencia existente"""
        try:
            attendance = Attendance.query.filter_by(external_id=external_id).first()

            if not attendance:
                return error_response("Asistencia no encontrada", code=404)

            if "status" in data:
                if data["status"] not in [Attendance.Status.PRESENT, Attendance.Status.ABSENT]:
                    return error_response("Estado inválido. Use: present, absent")
                attendance.status = data["status"]

            db.session.commit()

            return success_response(
                msg="Asistencia actualizada correctamente",
                data={
                    "external_id": attendance.external_id,
                    "participant_external_id": attendance.participant.external_id,
                    "schedule_external_id": attendance.schedule.external_id,
                    "date": attendance.date,
                    "status": attendance.status
                }
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def eliminar_asistencia(self, external_id):
        """Eliminar una asistencia"""
        try:
            attendance = Attendance.query.filter_by(external_id=external_id).first()

            if not attendance:
                return error_response("Asistencia no encontrada", code=404)

            data = {
                "external_id": attendance.external_id,
                "participant_external_id": attendance.participant.external_id,
                "schedule_external_id": attendance.schedule.external_id,
                "date": attendance.date,
                "status": attendance.status
            }

            db.session.delete(attendance)
            db.session.commit()

            return success_response(
                msg="Asistencia eliminada correctamente",
                data=data
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def obtener_resumen_por_participante(self, participant_external_id):
        """Obtener resumen de asistencias de un participante"""
        try:
            participant = Participant.query.filter_by(external_id=participant_external_id).first()
            if not participant:
                return error_response("Participante no encontrado", code=404)

            attendances = Attendance.query.filter_by(participant_id=participant.id).all()

            total = len(attendances)
            presentes = len([a for a in attendances if a.status == Attendance.Status.PRESENT])
            ausentes = len([a for a in attendances if a.status == Attendance.Status.ABSENT])
            porcentaje = round((presentes / total * 100), 2) if total > 0 else 0

            return success_response(
                msg="Resumen obtenido correctamente",
                data={
                    "participant_external_id": participant_external_id,
                    "total_sessions": total,
                    "present": presentes,
                    "absent": ausentes,
                    "attendance_percentage": porcentaje
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")
