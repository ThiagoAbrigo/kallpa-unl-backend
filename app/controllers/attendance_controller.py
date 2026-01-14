from datetime import date
from app.models.attendance import Attendance
from app.models.participant import Participant
from app.models.schedule import Schedule
from app.utils.responses import error_response, success_response
from app import db
from datetime import datetime


class AttendanceController:

    def register_attendance(self, data):
        """Registrar una asistencia individual"""
        try:
            campos = ["participant_external_id", "schedule_external_id", "status"]
            for campo in campos:
                if campo not in data:
                    return error_response(f"Falta el campo requerido: {campo}")

            valid_statuses = [Attendance.Status.PRESENT, Attendance.Status.ABSENT]
            if data["status"] not in valid_statuses:
                return error_response(f"Estado inválido. Use: {valid_statuses}")

            participant = Participant.query.filter_by(
                external_id=data["participant_external_id"]
            ).first()
            if not participant:
                return error_response("Participante no encontrado", code=404)

            schedule = Schedule.query.filter_by(
                external_id=data["schedule_external_id"]
            ).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            fecha = data.get("date", date.today().isoformat())
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                return error_response("Formato de fecha inválido. Use YYYY-MM-DD")

            # Check duplicates
            existing_attendance = Attendance.query.filter_by(
                participant_id=participant.id,
                schedule_id=schedule.id,
                date=fecha
            ).first()
            if existing_attendance:
                 return error_response(f"El participante ya tiene asistencia registrada para esta fecha y horario")

            # Check capacity
            current_count = Attendance.query.filter_by(
                schedule_id=schedule.id,
                date=fecha,
                status=Attendance.Status.PRESENT 
            ).count()
            
            if current_count >= schedule.maxSlots:
                return error_response(f"Cupos llenos para esta sesión ({schedule.maxSlots} slots)")

            nuevo = Attendance(
                participant_id=participant.id,
                schedule_id=schedule.id,
                date=fecha,
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

    def get_participants(self, program=None):
        """Obtener todos los participantes, opcionalmente filtrados por programa"""
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
            return error_response(f"Error interno: {str(e)}")

    def get_schedules(self):
        """Obtener todos los horarios"""
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
                        "description": s.description
                    }
                )
            return success_response(msg="Horarios obtenidos correctamente", data=result)
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def create_schedule(self, data):
        """Crear un nuevo horario/sesión"""
        try:
            # Map camelCase inputs to snake_case if necessary
            name = data.get("name")
            day_of_week = data.get("day_of_week") or data.get("dayOfWeek")
            start_time = data.get("start_time") or data.get("startTime")
            end_time = data.get("end_time") or data.get("endTime")
            max_slots = data.get("max_slots") or data.get("maxSlots")
            program = data.get("program")
            
            # Campos opcionales de fecha
            specific_date = data.get("specific_date") or data.get("specificDate")
            start_date = data.get("start_date") or data.get("startDate")
            end_date = data.get("end_date") or data.get("endDate")
            is_recurring = data.get("is_recurring") if data.get("is_recurring") is not None else data.get("isRecurring")
            location = data.get("location")
            description = data.get("description")

            if not all([name, start_time, end_time, max_slots, program]):
                return error_response(f"Faltan campos requeridos")
            
            # Validar que tenga dayOfWeek O specificDate (al menos uno)
            if not day_of_week and not specific_date:
                return error_response("Se requiere dayOfWeek o specificDate")

            valid_programs = ["INICIACION", "FUNCIONAL"]
            if program not in valid_programs:
                return error_response(f"Programa inválido. Use: {valid_programs}")
            
            # Validar fechas no sean pasadas
            from datetime import date as date_class
            hoy = date_class.today().isoformat()
            
            if specific_date and specific_date < hoy:
                return error_response("No se puede crear sesión con fecha pasada")
            
            if start_date and start_date < hoy:
                return error_response("La fecha de inicio no puede ser anterior a hoy")
            
            if end_date and start_date and end_date < start_date:
                return error_response("La fecha de fin debe ser posterior a la fecha de inicio")

            valid_days = [
                "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"
            ]
            if day_of_week.upper() not in valid_days:
                return error_response(f"Día inválido. Use: {valid_days}")

            import re
            time_pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
            if not re.match(time_pattern, start_time) or not re.match(time_pattern, end_time):
               return error_response("Formato de hora inválido. Use HH:MM (24h)")
            
            if start_time >= end_time:
                return error_response("La hora de inicio debe ser menor a la hora de fin")

            if int(max_slots) <= 0:
                return error_response("El número de cupos debe ser mayor a 0")

            # Validate Overlaps
            overlaps = Schedule.query.filter(
                Schedule.dayOfWeek == day_of_week.upper(),
                Schedule.program == program,
                # (StartA < EndB) and (EndA > StartB)
                Schedule.startTime < end_time,
                Schedule.endTime > start_time
                # Assuming simple active check isnt needed or status field missing
            ).first()
            
            if overlaps:
                return error_response(f"El horario se solapa con otro existente: {overlaps.name}")

            nuevo_schedule = Schedule(
                name=name,
                dayOfWeek=day_of_week.upper(), # Store standardized
                startTime=start_time,
                endTime=end_time,
                maxSlots=max_slots,
                program=program,
                specificDate=specific_date,
                startDate=start_date,
                endDate=end_date,
                isRecurring=is_recurring if is_recurring is not None else (specific_date is None),
                location=location,
                description=description
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
            return error_response(f"Error creando horario: {str(e)}")

    def update_schedule(self, schedule_id, data):
        """Actualizar un horario"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

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
            return error_response(f"Error actualizando horario: {str(e)}")

    def delete_schedule(self, schedule_id):
        """Eliminar un horario"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)
            schedule.status = "inactive"
            db.session.commit()
            return success_response(msg="Horario eliminado correctamente (Soft Delete)")
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error eliminando horario: {str(e)}")

    def get_today_sessions(self):
        """Obtener las sesiones programadas para hoy"""
        try:
            from datetime import date as date_class
            dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            hoy_date = date_class.today().isoformat()
            hoy_dia = dias_semana[datetime.now().weekday()]

            # Obtener sesiones recurrentes del día Y sesiones con fecha específica de hoy
            schedules = Schedule.query.filter(
                Schedule.status == "active"
            ).filter(
                db.or_(
                    Schedule.dayOfWeek == hoy_dia,
                    Schedule.specificDate == hoy_date
                )
            ).all()
            
            result = []
            for s in schedules:
                # Verificar si ya tiene asistencias registradas para hoy
                attendances_count = Attendance.query.filter_by(
                    schedule_id=s.id,
                    date=hoy_date
                ).count()
                
                # Determinar el estado
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
                        "has_attendances": attendances_count > 0
                    }
                )
            return success_response(
                msg=f"Sesiones de hoy obtenidas correctamente", data=result
            )
        except Exception as e:
            return error_response(f"Error interno: {str(e)}")

    def get_history(
        self, date_from=None, date_to=None, schedule_id=None, day_filter=None
    ):
        """Obtener historial de asistencias con filtros"""
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
            return error_response(f"Error interno: {str(e)}")

    def register_public_attendance(self, data):
        """Registrar asistencia desde el frontend"""
        return self.register_bulk_attendance(data)

    def get_programs(self):
        """Obtener todos los programas (distinct list)"""
        try:
            programs = db.session.query(Schedule.program).distinct().all()
            result = [{"name": p[0]} for p in programs if p[0]]
            return success_response(msg="Programas obtenidos", data=result)
        except Exception as e:
            return error_response(f"Error obteniendo programas: {str(e)}")

    def get_session_detail(self, schedule_id, date):
        """Obtener detalle de asistencia de una sesión"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

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
            return error_response(f"Error: {str(e)}")

    def delete_session_attendance(self, schedule_id, date):
        """Eliminar asistencia de una sesión"""
        try:
            schedule = Schedule.query.filter_by(external_id=schedule_id).first()
            if not schedule:
                return error_response("Horario no encontrado", code=404)

            Attendance.query.filter_by(schedule_id=schedule.id, date=date).delete()
            db.session.commit()

            return success_response(
                msg="Registros de asistencia eliminados para la fecha"
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f"Error: {str(e)}")

    def _calculate_attendance_percentage(self, participant_id):
        """Calcula el porcentaje de asistencia de un participante"""
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

    def register_bulk_attendance(self, data):
        """Registrar múltiples asistencias de una sesión"""
        try:
            if "schedule_external_id" not in data:
                return error_response("Falta el campo: schedule_external_id")

            if "attendances" not in data or not isinstance(data["attendances"], list):
                return error_response(
                    "Falta el campo: attendances (debe ser una lista)"
                )

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
            return error_response(f"Error interno: {str(e)}")

    def get_daily_attendance_percentage(self, date_str=None):
        """Obtener la sesión con el porcentaje de asistencia más bajo del último día o fecha especificada"""
        try:
            from datetime import date as date_class

            # Si no se pasa fecha, buscamos la última fecha con registros
            if date_str:
                fecha = date_str
            else:
                # Traer la última fecha registrada en Attendance
                last_attendance = Attendance.query.order_by(Attendance.date.desc()).first()
                if last_attendance:
                    fecha = last_attendance.date
                else:
                    fecha = date_class.today().isoformat()  # fallback si no hay registros

            # Traer todas las sesiones activas
            schedules = Schedule.query.filter_by(status="active").all()
            result = []

            for s in schedules:
                total_attendances = Attendance.query.filter_by(
                    schedule_id=s.id, date=fecha
                ).count()
                
                present_count = Attendance.query.filter_by(
                    schedule_id=s.id, date=fecha, status=Attendance.Status.PRESENT
                ).count()

                percentage = round((present_count / total_attendances) * 100, 2) if total_attendances > 0 else 0

                result.append(
                    {
                        "schedule_external_id": s.external_id,
                        "schedule_name": s.name,
                        "date": fecha,
                        "total_registered": total_attendances,
                        "present": present_count,
                        "attendance_percentage": percentage,
                    }
                )

            if not result:
                return success_response(msg=f"No hay sesiones activas para el día {fecha}", data=[])

            # Seleccionar la sesión con el porcentaje más bajo
            lowest_attendance = min(result, key=lambda x: x["attendance_percentage"])

            return success_response(
                msg=f"Sesión con el porcentaje de asistencia más bajo del día {fecha}",
                data=[lowest_attendance]
            )

        except Exception as e:
            return error_response(f"Error interno: {str(e)}")
