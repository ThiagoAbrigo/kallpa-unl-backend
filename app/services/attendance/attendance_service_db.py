from app.models.attendance import Attendance
from app.models.participant import Participant
from app.models.schedule import Schedule
from app.models.program import Program
from app.utils.responses import success_response, error_response
from app import db
from datetime import date, datetime, timedelta
import uuid


class AttendanceServiceDB:

    def _calculate_date_for_schedule(self, schedule):
        """
        Calcular la fecha correcta para un schedule:
        - Si es específico (isRecurring=False), usa specificDate
        - Si es recurrente, calcula el próximo día que coincida con dayOfWeek dentro del rango start_date/end_date
        """
        today = date.today()
        today_str = today.isoformat()

        # Si es sesión específica
        if schedule.isRecurring == False and schedule.specificDate:
            return schedule.specificDate

        # Si es recurrente
        if schedule.dayOfWeek:
            day_map = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
            }
            target_day = day_map.get(schedule.dayOfWeek.lower())
            if target_day is None:
                return today_str

            current_day = today.weekday()

            # Si hay start_date definido, calcular desde ahí
            if schedule.startDate:
                start = datetime.strptime(schedule.startDate, "%Y-%m-%d").date()

                # Si start_date es futuro, calcular el primer día que coincida desde start_date
                if start > today:
                    start_day = start.weekday()
                    diff = target_day - start_day
                    if diff < 0:
                        diff += 7
                    target_date = start + timedelta(days=diff)
                else:
                    # Si ya pasó start_date, buscar el día más reciente (pasado o hoy)
                    diff = target_day - current_day
                    if diff > 0:
                        diff -= 7
                    target_date = today + timedelta(days=diff)

                    # Asegurar que no sea antes del start_date
                    if target_date < start:
                        target_date = start + timedelta(
                            days=(target_day - start.weekday() + 7) % 7
                        )

                # Verificar que esté dentro del rango end_date
                if schedule.endDate:
                    end = datetime.strptime(schedule.endDate, "%Y-%m-%d").date()
                    if target_date > end:
                        # Buscar el último día válido
                        diff = target_day - end.weekday()
                        if diff > 0:
                            diff -= 7
                        target_date = end + timedelta(days=diff)

                return target_date.isoformat()
            else:
                # Sin start_date, calcular el día más reciente
                diff = target_day - current_day
                if diff > 0:
                    diff -= 7
                target_date = today + timedelta(days=diff)
                return target_date.isoformat()

        return today_str

    def _calculate_date_for_weekday(self, day_of_week):
        """Calcular la fecha correspondiente al día de la semana del schedule (igual que el mock)"""
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        target_day = day_map.get(day_of_week.lower() if day_of_week else None)
        if target_day is None:
            return date.today().isoformat()

        today = date.today()
        current_day = today.weekday()

        # Calcular diferencia de días (buscamos el día más reciente, incluyendo hoy)
        diff = target_day - current_day
        if diff > 0:
            diff -= 7

        target_date = today + timedelta(days=diff)
        return target_date.isoformat()

    def register_attendance(self, data):
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
            participant = Participant.query.filter_by(
                external_id=data["participant_external_id"]
            ).first()
            if not participant:
                return error_response("Participante no encontrado", code=404)

            # Buscar schedule por external_id
            schedule = Schedule.query.filter_by(
                external_id=data["schedule_external_id"]
            ).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            nuevo = Attendance(
                participant_id=participant.id,
                schedule_id=schedule.id,
                date=data.get("date", date.today().isoformat()),
                status=data["status"],
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
                    "status": nuevo.status,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def register_bulk_attendance(self, data):
        """Registrar múltiples asistencias de una sesión"""
        try:
            if "schedule_external_id" not in data:
                return error_response("Falta el campo: schedule_external_id")

            if "attendances" not in data or not isinstance(data["attendances"], list):
                return error_response(
                    "Falta el campo: attendances (debe ser una lista)"
                )

            # Buscar schedule
            schedule = Schedule.query.filter_by(
                external_id=data["schedule_external_id"]
            ).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

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
                msg=f"Se registraron {len(registros_creados)} asistencias en BD",
                data={
                    "total": len(registros_creados),
                    "attendances": registros_creados,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def get_attendances(self, filters=None):
        """Obtener todas las asistencias con filtros opcionales"""
        try:
            query = Attendance.query

            if filters:
                if filters.get("participant_external_id"):
                    participant = Participant.query.filter_by(
                        external_id=filters["participant_external_id"]
                    ).first()
                    if participant:
                        query = query.filter_by(participant_id=participant.id)
                if filters.get("schedule_external_id"):
                    schedule = Schedule.query.filter_by(
                        external_id=filters["schedule_external_id"]
                    ).first()
                    if schedule:
                        query = query.filter_by(schedule_id=schedule.id)
                if filters.get("date"):
                    query = query.filter_by(date=filters["date"])
                if filters.get("status"):
                    query = query.filter_by(status=filters["status"])

            attendances = query.all()
            result = []
            for a in attendances:
                result.append(
                    {
                        "external_id": a.external_id,
                        "participant_external_id": a.participant.external_id,
                        "schedule_external_id": a.schedule.external_id,
                        "date": a.date,
                        "status": a.status,
                    }
                )

            return success_response(
                msg="Asistencias obtenidas correctamente", data=result
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def get_attendance_by_id(self, external_id):
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
                    "status": attendance.status,
                },
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def update_attendance(self, external_id, data):
        """Actualizar una asistencia existente"""
        try:
            attendance = Attendance.query.filter_by(external_id=external_id).first()

            if not attendance:
                return error_response("Asistencia no encontrada", code=404)

            if "status" in data:
                if data["status"] not in [
                    Attendance.Status.PRESENT,
                    Attendance.Status.ABSENT,
                ]:
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
                    "status": attendance.status,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def delete_attendance(self, external_id):
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
                "status": attendance.status,
            }

            db.session.delete(attendance)
            db.session.commit()

            return success_response(msg="Asistencia eliminada correctamente", data=data)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def get_participant_summary(self, participant_external_id):
        """Obtener resumen de asistencias de un participante"""
        try:
            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()
            if not participant:
                return error_response("Participante no encontrado", code=404)

            attendances = Attendance.query.filter_by(
                participant_id=participant.id
            ).all()

            total = len(attendances)
            presentes = len(
                [a for a in attendances if a.status == Attendance.Status.PRESENT]
            )
            ausentes = len(
                [a for a in attendances if a.status == Attendance.Status.ABSENT]
            )
            porcentaje = round((presentes / total * 100), 2) if total > 0 else 0

            return success_response(
                msg="Resumen obtenido correctamente",
                data={
                    "participant_external_id": participant_external_id,
                    "total_sessions": total,
                    "present": presentes,
                    "absent": ausentes,
                    "attendance_percentage": porcentaje,
                },
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    # ========== MÉTODOS PÚBLICOS PARA EL FRONTEND ==========

    def get_participants(self):
        """Obtener todos los participantes"""
        try:
            participants = Participant.query.all()
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
                    }
                )
            return success_response(
                msg="Participantes obtenidos correctamente", data=result
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def get_schedules(self):
        """Obtener todos los horarios"""
        try:
            schedules = Schedule.query.all()
            result = []
            for s in schedules:
                result.append(
                    {
                        "external_id": s.external_id,
                        "name": s.name,
                        "day_of_week": s.dayOfWeek,
                        "start_time": s.startTime,
                        "end_time": s.endTime,
                        "program_id": s.program_id,
                        "start_date": s.startDate,
                        "end_date": s.endDate,
                        "specific_date": s.specificDate,
                        "is_recurring": (
                            s.isRecurring if s.isRecurring is not None else True
                        ),
                        "location": s.location,
                        "capacity": s.maxSlots,
                        "description": s.description,
                    }
                )
            return success_response(msg="Horarios obtenidos correctamente", data=result)
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def get_today_sessions(self):
        """Obtener las sesiones programadas para hoy"""
        try:
            weekdays_en = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            weekdays_es = [
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes",
                "Sábado",
                "Domingo",
            ]
            today = date.today()
            today_str = today.isoformat()
            today_weekday_en = weekdays_en[today.weekday()]
            today_weekday_es = weekdays_es[today.weekday()]

            sessions = []
            participants_count = Participant.query.count()

            # Obtener todas las sesiones
            all_schedules = Schedule.query.all()

            for s in all_schedules:
                should_include = False

                # Si es sesión específica, verificar la fecha específica
                if s.isRecurring == False and s.specificDate:
                    should_include = s.specificDate == today_str
                # Si es recurrente, verificar día de la semana y rango de fechas
                elif s.dayOfWeek and s.dayOfWeek.lower() == today_weekday_en.lower():
                    # Verificar si estamos dentro del rango de fechas
                    if s.startDate and s.endDate:
                        should_include = s.startDate <= today_str <= s.endDate
                    else:
                        should_include = True

                if not should_include:
                    continue

                # Contar asistencias de hoy para este schedule
                attendance_count = (
                    Attendance.query.filter_by(schedule_id=s.id)
                    .filter(Attendance.date == today_str)
                    .filter(Attendance.status == "present")
                    .count()
                )

                # Obtener nombre del programa
                program_name = ""
                if s.program_id:
                    program = Program.query.get(s.program_id)
                    program_name = program.name if program else ""

                sessions.append(
                    {
                        "id": s.id,
                        "schedule_id": s.external_id,
                        "external_id": s.external_id,
                        "name": s.name,
                        "start_time": s.startTime,
                        "end_time": s.endTime,
                        "program_name": program_name,
                        "location": s.location or "",
                        "attendance_count": attendance_count,
                        "participant_count": participants_count,
                        "is_recurring": (
                            s.isRecurring if s.isRecurring is not None else True
                        ),
                        "start_date": s.startDate,
                        "end_date": s.endDate,
                        "specific_date": s.specificDate,
                    }
                )

            return success_response(
                msg=f"Sesiones de hoy ({today_weekday_es}) obtenidas correctamente",
                data={"date": today_str, "day": today_weekday_es, "sessions": sessions},
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def get_history(
        self, date_from=None, date_to=None, schedule_id=None, day_filter=None
    ):
        """Obtener historial de asistencias agrupado por sesión/fecha (igual que el mock)"""
        try:
            query = Attendance.query

            if date_from:
                query = query.filter(Attendance.date >= date_from)
            if date_to:
                query = query.filter(Attendance.date <= date_to)

            # Filtrar por schedule_id si se proporciona
            if schedule_id:
                schedule = Schedule.query.filter_by(external_id=schedule_id).first()
                if schedule:
                    query = query.filter(Attendance.schedule_id == schedule.id)

            attendances = query.order_by(Attendance.date.desc()).all()

            # Filtrar por día de la semana si se proporciona
            if day_filter and day_filter.lower() != "todos los días":
                day_map_es_to_en = {
                    "lunes": "monday",
                    "martes": "tuesday",
                    "miércoles": "wednesday",
                    "miercoles": "wednesday",
                    "jueves": "thursday",
                    "viernes": "friday",
                    "sábado": "saturday",
                    "sabado": "saturday",
                    "domingo": "sunday",
                }
                day_en = day_map_es_to_en.get(day_filter.lower(), day_filter.lower())

                # Función para obtener el día de la semana de una fecha
                def get_day_of_week_from_date(date_str):
                    from datetime import datetime

                    days_en = [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ]
                    try:
                        date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
                        return days_en[date_obj.weekday()]
                    except:
                        return None

                # Filtrar: usar dayOfWeek del schedule, o inferir del specificDate, o de la fecha del attendance
                def matches_day(a):
                    # Primero intentar con dayOfWeek del schedule
                    if a.schedule.dayOfWeek:
                        return a.schedule.dayOfWeek.lower() == day_en
                    # Si no hay dayOfWeek, inferir de specificDate del schedule
                    if a.schedule.specificDate:
                        inferred_day = get_day_of_week_from_date(
                            a.schedule.specificDate
                        )
                        return inferred_day == day_en
                    # Si no hay specificDate, inferir de la fecha del attendance
                    if a.date:
                        inferred_day = get_day_of_week_from_date(a.date)
                        return inferred_day == day_en
                    return False

                attendances = [a for a in attendances if matches_day(a)]

            # Función para obtener el día de la semana (mover fuera del if para reutilizar)
            def get_day_of_week(schedule, attendance_date):
                from datetime import datetime

                days_en = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]
                # Primero usar dayOfWeek del schedule si existe
                if schedule.dayOfWeek:
                    return schedule.dayOfWeek
                # Si no, inferir de specificDate
                if schedule.specificDate:
                    try:
                        date_obj = datetime.strptime(
                            str(schedule.specificDate), "%Y-%m-%d"
                        )
                        return days_en[date_obj.weekday()]
                    except:
                        pass
                # Si no, inferir de la fecha del attendance
                if attendance_date:
                    try:
                        date_obj = datetime.strptime(str(attendance_date), "%Y-%m-%d")
                        return days_en[date_obj.weekday()]
                    except:
                        pass
                return None

            # Agrupar por schedule_id y fecha (igual que el mock)
            grouped = {}
            for a in attendances:
                key = f"{a.schedule.external_id}_{a.date}"
                if key not in grouped:
                    grouped[key] = {
                        "schedule_id": a.schedule.external_id,
                        "schedule_name": a.schedule.name,
                        "date": a.date,
                        "day_of_week": get_day_of_week(a.schedule, a.date),
                        "start_time": a.schedule.startTime,
                        "end_time": a.schedule.endTime,
                        "presentes": 0,
                        "ausentes": 0,
                        "total": 0,
                    }

                grouped[key]["total"] += 1
                if a.status == "present":
                    grouped[key]["presentes"] += 1
                else:
                    grouped[key]["ausentes"] += 1

            history = list(grouped.values())
            # Ordenar por fecha descendente
            history.sort(key=lambda x: x.get("date", ""), reverse=True)

            return success_response(
                msg="Historial obtenido correctamente", data=history
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def register_public_attendance(self, data):
        """Registrar asistencia desde el frontend"""
        try:
            if not data:
                return error_response("No se enviaron datos")

            schedule_id = data.get("schedule_id")
            if not schedule_id:
                return error_response("Falta el campo: schedule_id")

            # Buscar schedule por external_id
            schedule = Schedule.query.filter_by(external_id=str(schedule_id)).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            # Calcular la fecha usando el nuevo método que considera start_date, end_date y specific_date
            attendance_date = self._calculate_date_for_schedule(schedule)

            # Soportar ambos formatos
            attendances = data.get("attendance", {})
            input_records = data.get("records", [])

            if input_records and isinstance(input_records, list):
                attendances = {}
                for r in input_records:
                    pid = str(r.get("participant_id", ""))
                    status = r.get("status", "PRESENT")
                    attendances[pid] = status

            if not attendances:
                return error_response("Falta el campo: attendance o records")

            count = 0
            for participant_id, status in attendances.items():
                participant = Participant.query.filter_by(
                    external_id=str(participant_id)
                ).first()
                if not participant:
                    continue

                # Verificar si ya existe
                existing = Attendance.query.filter_by(
                    participant_id=participant.id,
                    schedule_id=schedule.id,
                    date=attendance_date,
                ).first()

                status_value = status.lower() if isinstance(status, str) else status

                if existing:
                    existing.status = status_value
                else:
                    nuevo = Attendance(
                        participant_id=participant.id,
                        schedule_id=schedule.id,
                        date=attendance_date,
                        status=status_value,
                    )
                    db.session.add(nuevo)
                count += 1

            db.session.commit()

            return success_response(
                msg=f"Asistencia registrada correctamente",
                data={
                    "total": count,
                    "date": attendance_date,
                    "schedule_id": schedule_id,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def get_programs(self):
        """Obtener todos los programas"""
        try:
            programs = Program.query.all()
            result = []
            for p in programs:
                result.append(
                    {
                        "id": p.id,
                        "name": p.name,
                        "external_id": getattr(p, "external_id", f"prog-{p.id}"),
                    }
                )
            return success_response(
                msg="Programas obtenidos correctamente", data=result
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def get_session_detail(self, schedule_id, attendance_date):
        """Obtener detalle de asistencia de una sesión específica"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            attendances = Attendance.query.filter_by(
                schedule_id=schedule.id, date=attendance_date
            ).all()

            records = []
            for a in attendances:
                p = a.participant
                records.append(
                    {
                        "external_id": a.external_id,
                        "participant_id": p.external_id,
                        "participant_name": f"{p.firstName} {p.lastName}".strip(),
                        "dni": p.dni,
                        "status": a.status.upper() if a.status else "",
                    }
                )

            present_count = len([r for r in records if r.get("status") == "PRESENT"])
            absent_count = len(
                [r for r in records if r.get("status") in ["ABSENT", "JUSTIFIED"]]
            )

            return success_response(
                msg="Detalle de sesión obtenido correctamente",
                data={
                    "schedule_id": schedule_id,
                    "date": attendance_date,
                    "schedule": {
                        "external_id": schedule.external_id,
                        "day_of_week": schedule.dayOfWeek,
                        "start_time": schedule.startTime,
                        "end_time": schedule.endTime,
                    },
                    "records": records,
                    "stats": {
                        "presentes": present_count,
                        "ausentes": absent_count,
                        "total": len(records),
                    },
                    "total": len(records),
                    "present": present_count,
                    "absent": absent_count,
                },
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def delete_session_attendance(self, schedule_id, attendance_date):
        """Eliminar asistencia de una sesión específica"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            attendances = Attendance.query.filter_by(
                schedule_id=schedule.id, date=attendance_date
            ).all()

            if not attendances:
                return error_response(
                    "No se encontraron registros para eliminar", code=404
                )

            deleted_count = len(attendances)
            for a in attendances:
                db.session.delete(a)

            db.session.commit()

            return success_response(
                msg=f"Se eliminaron {deleted_count} registros de asistencia",
                data={
                    "deleted": deleted_count,
                    "schedule_id": schedule_id,
                    "date": attendance_date,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def create_schedule(self, data):
        """Crear un nuevo horario/sesión"""
        try:
            if not data:
                return error_response("No se enviaron datos")

            name = data.get("name") or data.get("nombre")
            day = data.get("day_of_week") or data.get("dia")
            start_time = data.get("start_time") or data.get("hora_inicio")
            end_time = data.get("end_time") or data.get("hora_fin")
            program_id = data.get("program_id", 1)
            max_slots = data.get("max_slots") or data.get("capacity", 30)

            # Nuevos campos
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            specific_date = data.get("specific_date")
            is_recurring = data.get("is_recurring", True)
            location = data.get("location")
            description = data.get("description")

            if not name:
                return error_response("Falta el campo: name/nombre")
            if not start_time:
                return error_response("Falta el campo: start_time/hora_inicio")
            if not end_time:
                return error_response("Falta el campo: end_time/hora_fin")

            # Mapear día a inglés si se proporciona
            day_of_week = None
            if day:
                day_map = {
                    "lunes": "monday",
                    "martes": "tuesday",
                    "miercoles": "wednesday",
                    "miércoles": "wednesday",
                    "jueves": "thursday",
                    "viernes": "friday",
                    "sabado": "saturday",
                    "sábado": "saturday",
                    "domingo": "sunday",
                }
                day_of_week = day_map.get(day.lower(), day.lower())

            nuevo = Schedule(
                name=name,
                dayOfWeek=day_of_week,
                startTime=start_time,
                endTime=end_time,
                maxSlots=max_slots,
                program_id=program_id,
                startDate=start_date,
                endDate=end_date,
                specificDate=specific_date,
                isRecurring=is_recurring,
                location=location,
                description=description,
            )

            db.session.add(nuevo)
            db.session.commit()

            return success_response(
                msg="Horario creado correctamente",
                data={
                    "external_id": nuevo.external_id,
                    "name": name,
                    "day_of_week": nuevo.dayOfWeek,
                    "start_time": nuevo.startTime,
                    "end_time": nuevo.endTime,
                    "program_id": nuevo.program_id,
                    "start_date": nuevo.startDate,
                    "end_date": nuevo.endDate,
                    "specific_date": nuevo.specificDate,
                    "is_recurring": nuevo.isRecurring,
                    "location": nuevo.location,
                    "capacity": nuevo.maxSlots,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def update_schedule(self, schedule_id, data):
        """Actualizar un horario/sesión"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            if data.get("name"):
                schedule.name = data.get("name")
            if data.get("day_of_week"):
                day = data.get("day_of_week")
                day_map = {
                    "lunes": "monday",
                    "martes": "tuesday",
                    "miercoles": "wednesday",
                    "miércoles": "wednesday",
                    "jueves": "thursday",
                    "viernes": "friday",
                    "sabado": "saturday",
                    "sábado": "saturday",
                    "domingo": "sunday",
                }
                schedule.dayOfWeek = day_map.get(day.lower(), day.lower())
            if data.get("start_time"):
                schedule.startTime = data.get("start_time")
            if data.get("end_time"):
                schedule.endTime = data.get("end_time")
            if data.get("program_id"):
                schedule.program_id = data.get("program_id")

            # Nuevos campos
            if "start_date" in data:
                schedule.startDate = data.get("start_date")
            if "end_date" in data:
                schedule.endDate = data.get("end_date")
            if "specific_date" in data:
                schedule.specificDate = data.get("specific_date")
            if "is_recurring" in data:
                schedule.isRecurring = data.get("is_recurring")
            if "location" in data:
                schedule.location = data.get("location")
            if "description" in data:
                schedule.description = data.get("description")
            if data.get("capacity") or data.get("max_slots"):
                schedule.maxSlots = data.get("capacity") or data.get("max_slots")

            db.session.commit()

            return success_response(
                msg="Horario actualizado correctamente",
                data={
                    "external_id": schedule.external_id,
                    "name": schedule.name,
                    "day_of_week": schedule.dayOfWeek,
                    "start_time": schedule.startTime,
                    "end_time": schedule.endTime,
                    "program_id": schedule.program_id,
                    "start_date": schedule.startDate,
                    "end_date": schedule.endDate,
                    "specific_date": schedule.specificDate,
                    "is_recurring": schedule.isRecurring,
                    "location": schedule.location,
                    "capacity": schedule.maxSlots,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def delete_schedule(self, schedule_id):
        """Eliminar un horario/sesión"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            # Eliminar asistencias asociadas
            Attendance.query.filter_by(schedule_id=schedule.id).delete()

            db.session.delete(schedule)
            db.session.commit()

            return success_response(
                msg="Horario eliminado correctamente", data={"external_id": schedule_id}
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno: {str(e)}")

    def calculate_attendance_average(self, attendances):
        if not attendances:
            return 0

        # participantes únicos
        total_participants = len({
            a["participant_external_id"] for a in attendances
        })

        if total_participants == 0:
            return 0

        total_present = sum(
            1 for a in attendances if a["status"] == "PRESENTE"
        )

        average = (total_present / total_participants) * 100
        return round(average, 2)
