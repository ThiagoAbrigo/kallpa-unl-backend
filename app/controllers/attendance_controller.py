from datetime import date, datetime
from app.models.attendance import Attendance
from app.models.participant import Participant
from app.models.schedule import Schedule
from app.utils.responses import error_response, success_response
from app import db


class AttendanceController:

    def get_participants(self, program=None):
        # Lista participantes activos con porcentaje de asistencia calculado
        try:
            query = Participant.query
            if program:
                query = query.filter_by(program=program)

            participants = query.all()
            result = []
            for p in participants:
                result.append(
                    {
                        "external_id": p.external_id,
                        "first_name": p.firstName,
                        "last_name": p.lastName,
                        "dni": p.dni,
                        "email": getattr(p, "email", None),
                        "phone": getattr(p, "phone", None),
                        "status": getattr(p, "status", "active"),
                        "program": getattr(p, "program", None),
                        "attendance_percentage": self._calculate_attendance_percentage(
                            p.id
                        ),
                    }
                )
            return success_response(
                msg="Participantes obtenidos correctamente", data=result
            )
        except Exception as e:
            return error_response(msg="Error interno", code=500, data={"error": str(e)})

    def get_schedules(self):
        # Retorna horarios/sesiones activas del sistema
        try:
            schedules = Schedule.query.filter_by(status="active").all()
            result = []
            for s in schedules:
                result.append(
                    {
                        "external_id": s.external_id,
                        "name": s.name,
                        "day_of_week": s.dayOfWeek,
                        "start_time": s.startTime,
                        "end_time": s.endTime,
                        "max_slots": s.maxSlots,
                        "program": s.program,
                        "specific_date": s.specificDate,
                        "start_date": s.startDate,
                        "end_date": s.endDate,
                        "is_recurring": s.isRecurring,
                        "location": s.location,
                        "description": s.description,
                    }
                )
            return success_response(msg="Horarios obtenidos correctamente", data=result)
        except Exception as e:
            return error_response(msg="Error interno", code=500, data={"error": str(e)})

    def create_schedule(self, data):
        # Crea nueva sesión con validaciones de horario, capacidad y solapamiento
        try:
            errors = {}

            # Mapeo de campos del frontend (camelCase -> snake_case)
            name = data.get("name")
            day_of_week = data.get("day_of_week") or data.get("dayOfWeek")
            start_time = data.get("start_time") or data.get("startTime")
            end_time = data.get("end_time") or data.get("endTime")
            max_slots = data.get("max_slots") or data.get("maxSlots")
            program = data.get("program")

            # Campos para sesiones específicas o recurrentes
            specific_date = data.get("specific_date") or data.get("specificDate")
            start_date = data.get("start_date") or data.get("startDate")
            end_date = data.get("end_date") or data.get("endDate")
            is_recurring = (
                data.get("is_recurring")
                if data.get("is_recurring") is not None
                else data.get("isRecurring")
            )
            location = data.get("location")
            description = data.get("description")

            # Validación de campos obligatorios
            if not name:
                errors["name"] = "El nombre es requerido"
            if not start_time:
                errors["start_time"] = "La hora de inicio es requerida"
            if not end_time:
                errors["end_time"] = "La hora de fin es requerida"
            if not max_slots:
                errors["max_slots"] = "El número de cupos es requerido"
            if not program:
                errors["program"] = "El programa es requerido"

            # Validar que tenga dayOfWeek O specificDate (al menos uno)
            if not day_of_week and not specific_date:
                errors["day_of_week"] = (
                    "Debe seleccionar un día de la semana o una fecha específica"
                )

            # Validar programa
            valid_programs = ["INICIACION", "FUNCIONAL"]
            if program and program not in valid_programs:
                errors["program"] = (
                    f"Programa inválido. Use: {', '.join(valid_programs)}"
                )

            # Validar día de la semana
            valid_days = [
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
            ]
            if day_of_week and day_of_week.upper() not in valid_days:
                errors["day_of_week"] = f"Día inválido. Use: {', '.join(valid_days)}"

            # Validar formato de horas
            import re

            time_pattern = r"^([01]\d|2[0-3]):([0-5]\d)$"
            if start_time and not re.match(time_pattern, start_time):
                errors["start_time"] = "Formato de hora inválido. Use HH:MM (24h)"
            if end_time and not re.match(time_pattern, end_time):
                errors["end_time"] = "Formato de hora inválido. Use HH:MM (24h)"

            # Validar que hora de inicio sea menor a hora de fin
            if start_time and end_time and start_time >= end_time:
                errors["time"] = "La hora de inicio debe ser menor a la hora de fin"

            # Validar cupos
            if max_slots:
                try:
                    if int(max_slots) <= 0:
                        errors["max_slots"] = "El número de cupos debe ser mayor a 0"
                except (ValueError, TypeError):
                    errors["max_slots"] = "El número de cupos debe ser numérico"

            # Validar fechas
            from datetime import date as date_class

            hoy = date_class.today().isoformat()

            if specific_date and specific_date < hoy:
                errors["specific_date"] = "No se puede crear sesión con fecha pasada"

            if start_date and start_date < hoy:
                errors["start_date"] = "La fecha de inicio no puede ser anterior a hoy"

            if end_date and start_date and end_date < start_date:
                errors["end_date"] = (
                    "La fecha de fin debe ser posterior a la fecha de inicio"
                )

            # Retornar si hay errores de validación
            if errors:
                return error_response(msg="Error de validación", data=errors, code=400)

            # Validación de solapamiento de horarios para sesiones recurrentes
            if day_of_week:
                overlaps = Schedule.query.filter(
                    Schedule.dayOfWeek == day_of_week.upper(),
                    Schedule.program == program,
                    Schedule.startTime < end_time,
                    Schedule.endTime > start_time,
                ).first()

                if overlaps:
                    return error_response(
                        msg="Error de validación",
                        data={
                            "schedule": f"El horario se solapa con otro existente: {overlaps.name}"
                        },
                        code=400,
                    )

            nuevo_schedule = Schedule(
                name=name,
                dayOfWeek=day_of_week.upper() if day_of_week else None,
                startTime=start_time,
                endTime=end_time,
                maxSlots=max_slots,
                program=program,
                specificDate=specific_date,
                startDate=start_date,
                endDate=end_date,
                isRecurring=(
                    is_recurring
                    if is_recurring is not None
                    else (specific_date is None)
                ),
                location=location,
                description=description,
            )
            db.session.add(nuevo_schedule)
            db.session.commit()

            return success_response(
                msg="Horario creado exitosamente",
                data={
                    "external_id": nuevo_schedule.external_id,
                    "name": nuevo_schedule.name,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(
                msg="Error creando horario", code=500, data={"error": str(e)}
            )

    def update_schedule(self, schedule_id, data):
        # Actualiza campos de sesión existente
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response(msg="Horario no encontrado", data={}, code=404)

            if "name" in data:
                schedule.name = data["name"]

            day_of_week = data.get("day_of_week") or data.get("dayOfWeek")
            if day_of_week:
                schedule.dayOfWeek = day_of_week

            start_time = data.get("start_time") or data.get("startTime")
            if start_time:
                schedule.startTime = start_time

            end_time = data.get("end_time") or data.get("endTime")
            if end_time:
                schedule.endTime = end_time

            max_slots = data.get("max_slots") or data.get("maxSlots")
            if max_slots:
                schedule.maxSlots = max_slots

            if "program" in data:
                schedule.program = data["program"]

            db.session.commit()
            return success_response(
                msg="Horario actualizado correctamente",
                data={"external_id": schedule.external_id},
            )
        except Exception as e:
            db.session.rollback()
            return error_response(
                msg="Error actualizando horario", code=500, data={"error": str(e)}
            )

    def delete_schedule(self, schedule_id):
        # Eliminación lógica: marca sesión como inactiva
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response(
                    msg="Horario no encontrado",
                    code=404,
                    data={"schedule_external_id": schedule_id},
                )
            schedule.status = "inactive"
            db.session.commit()
            return success_response(msg="Horario eliminado correctamente (Soft Delete)")
        except Exception as e:
            db.session.rollback()
            return error_response(
                msg="Error eliminando horario", code=500, data={"error": str(e)}
            )

    def get_today_sessions(self):
        # Obtiene sesiones programadas para hoy: recurrentes + fecha específica
        try:
            from datetime import date as date_class

            # Mapeo de días: 0=Lunes, 1=Martes, ... 6=Domingo
            dias_semana = [
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes",
                "Sábado",
                "Domingo",
            ]
            hoy_date = date_class.today().isoformat()
            hoy_dia = dias_semana[datetime.now().weekday()]

            # Consulta: sesiones recurrentes del día + sesiones específicas de hoy
            schedules = (
                Schedule.query.filter(Schedule.status == "active")
                .filter(
                    db.or_(
                        Schedule.dayOfWeek == hoy_dia, Schedule.specificDate == hoy_date
                    )
                )
                .all()
            )

            result = []
            for s in schedules:
                # Determinar estado: completada si ya tiene asistencias registradas
                attendances_count = Attendance.query.filter_by(
                    schedule_id=s.id, date=hoy_date
                ).count()

                status = "completada" if attendances_count > 0 else "pendiente"

                result.append(
                    {
                        "external_id": s.external_id,
                        "name": s.name,
                        "day_of_week": s.dayOfWeek,
                        "start_time": s.startTime,
                        "end_time": s.endTime,
                        "program": s.program,
                        "specific_date": s.specificDate,
                        "is_recurring": s.isRecurring,
                        "location": s.location,
                        "status": status,
                        "attendances_registered": attendances_count,
                        "has_attendances": attendances_count > 0,
                    }
                )
            return success_response(
                msg=f"Sesiones de hoy obtenidas correctamente", data=result
            )
        except Exception as e:
            return error_response(msg="Error interno", code=500, data={"error": str(e)})

    def get_history(
        self, date_from=None, date_to=None, schedule_id=None, day_filter=None
    ):
        # Historial de asistencias con filtros de fecha, sesión y día
        try:
            query = Attendance.query.join(Schedule).join(Participant)

            if date_from:
                query = query.filter(Attendance.date >= date_from)
            if date_to:
                query = query.filter(Attendance.date <= date_to)

            if schedule_id:
                schedule = Schedule.query.filter_by(external_id=schedule_id).first()
                if schedule:
                    query = query.filter(Attendance.schedule_id == schedule.id)

            if day_filter:
                query = query.filter(Schedule.dayOfWeek == day_filter)

            attendances = query.order_by(Attendance.date.desc()).all()
            result = []
            for a in attendances:
                result.append(
                    {
                        "external_id": a.external_id,
                        "date": a.date,
                        "status": a.status,
                        "participant": {
                            "external_id": a.participant.external_id,
                            "first_name": a.participant.firstName,
                            "last_name": a.participant.lastName,
                            "dni": a.participant.dni,
                        },
                        "schedule": {
                            "external_id": a.schedule.external_id,
                            "name": a.schedule.name,
                            "day_of_week": a.schedule.dayOfWeek,
                            "start_time": a.schedule.startTime,
                            "end_time": a.schedule.endTime,
                            "program": a.schedule.program,
                        },
                    }
                )
            return success_response(msg="Historial obtenido correctamente", data=result)
        except Exception as e:
            return error_response(msg="Error interno", code=500, data={"error": str(e)})

    def get_session_detail(self, schedule_id, date):
        # Detalle completo de participantes y estados de una sesión específica
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response(msg="Horario no encontrado", data={}, code=404)

            attendances = Attendance.query.filter_by(
                schedule_id=schedule.id, date=date
            ).all()

            result = []
            for a in attendances:
                result.append(
                    {
                        "participant_external_id": a.participant.external_id,
                        "status": a.status,
                        "participant_name": f"{a.participant.firstName} {a.participant.lastName}",
                        "participant": {
                            "external_id": a.participant.external_id,
                            "first_name": a.participant.firstName,
                            "last_name": a.participant.lastName,
                            "dni": a.participant.dni,
                            "email": getattr(a.participant, "email", None),
                            "img": "https://i.pravatar.cc/150?u="
                            + a.participant.external_id,
                        },
                    }
                )

            return success_response(msg="Detalle de sesión obtenido", data=result)
        except Exception as e:
            return error_response(msg="Error", code=500, data={"error": str(e)})

    def delete_session_attendance(self, schedule_id, date):
        # Elimina todos los registros de asistencia de una fecha específica
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response(
                    msg="Horario no encontrado",
                    code=404,
                    data={"schedule_external_id": schedule_id},
                )

            Attendance.query.filter_by(schedule_id=schedule.id, date=date).delete()
            db.session.commit()

            return success_response(
                msg="Registros de asistencia eliminados para la fecha"
            )
        except Exception as e:
            db.session.rollback()
            return error_response(msg="Error", code=500, data={"error": str(e)})

    def _calculate_attendance_percentage(self, participant_id):
        # Método interno: calcula porcentaje de asistencias de un participante
        try:
            total = Attendance.query.filter_by(participant_id=participant_id).count()
            if total == 0:
                return 0
            present = Attendance.query.filter_by(
                participant_id=participant_id, status=Attendance.Status.PRESENT
            ).count()
            return round((present / total) * 100, 2)
        except:
            return 0

    def register_public_attendance(self, data):
        # Endpoint público que utiliza registro masivo
        return self.register_bulk_attendance(data)

    def register_bulk_attendance(self, data):
        # Registro masivo de asistencias para una sesión completa
        try:
            if "schedule_external_id" not in data:
                return error_response(
                    msg="Error de validación",
                    code=400,
                    data={
                        "schedule_external_id": "El campo schedule_external_id es requerido"
                    },
                )

            if "attendances" not in data or not isinstance(data["attendances"], list):
                return error_response(
                    msg="Error de validación",
                    code=400,
                    data={
                        "attendances": "El campo attendances es requerido y debe ser una lista"
                    },
                )

            schedule = Schedule.query.filter_by(
                external_id=data["schedule_external_id"]
            ).first()
            if not schedule:
                return error_response(
                    msg="Horario no encontrado",
                    code=404,
                    data={"schedule_external_id": data.get("schedule_external_id")},
                )

            fecha = data.get("date", date.today().isoformat())
            registros_creados = []

            for item in data["attendances"]:
                if "participant_external_id" not in item or "status" not in item:
                    continue

                participant = Participant.query.filter_by(
                    external_id=item["participant_external_id"]
                ).first()
                if not participant:
                    continue

                existing = Attendance.query.filter_by(
                    participant_id=participant.id, schedule_id=schedule.id, date=fecha
                ).first()

                if existing:
                    existing.status = item["status"]
                else:
                    nuevo = Attendance(
                        participant_id=participant.id,
                        schedule_id=schedule.id,
                        date=fecha,
                        status=item["status"],
                    )
                    db.session.add(nuevo)

                registros_creados.append(
                    {
                        "participant_external_id": item["participant_external_id"],
                        "status": item["status"],
                    }
                )

            db.session.commit()

            return success_response(
                msg=f"Se procesaron {len(registros_creados)} asistencias",
                data={
                    "total": len(registros_creados),
                    "attendances": registros_creados,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(msg="Error interno", code=500, data={"error": str(e)})
