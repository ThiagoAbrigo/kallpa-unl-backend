import json
import os
from app.utils.responses import success_response, error_response
import uuid
from datetime import date, timedelta


class AttendanceServiceMock:

    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.mock_path = os.path.join(base, "mock", "attendance.json")
        self.participants_path = os.path.join(base, "mock", "participants.json")
        self.schedules_path = os.path.join(base, "mock", "schedules.json")

        for path in [self.mock_path, self.participants_path, self.schedules_path]:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)

    def _load(self, path=None):
        if path is None:
            path = self.mock_path
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data, path=None):
        if path is None:
            path = self.mock_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def register_attendance(self, data):
        """Registrar una asistencia individual"""
        if not data:
            return error_response("No se enviaron datos")

        required_fields = ["participant_external_id", "schedule_external_id", "status"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Falta el campo requerido: {field}")

        valid_statuses = ["present", "absent"]
        if data["status"] not in valid_statuses:
            return error_response(f"Estado inválido. Use: {valid_statuses}")

        try:
            records = self._load()

            attendance = {
                "external_id": str(uuid.uuid4()),
                "participant_external_id": data["participant_external_id"],
                "schedule_external_id": data["schedule_external_id"],
                "date": data.get("date", date.today().isoformat()),
                "status": data["status"]
            }

            records.append(attendance)
            self._save(records)

            return success_response(
                msg="Asistencia registrada correctamente (MOCK)",
                data=attendance
            )
        except Exception as e:
            return error_response(f"Error interno al guardar la asistencia: {e}")

    def register_bulk_attendance(self, data):
        """Registrar múltiples asistencias de una sesión"""
        if not data:
            return error_response("No se enviaron datos")

        if "schedule_external_id" not in data:
            return error_response("Falta el campo: schedule_external_id")
        
        if "attendances" not in data or not isinstance(data["attendances"], list):
            return error_response("Falta el campo: attendances (debe ser una lista)")

        try:
            records = self._load()
            attendance_date = data.get("date", date.today().isoformat())
            schedule_external_id = data["schedule_external_id"]
            
            created_records = []

            for item in data["attendances"]:
                if "participant_external_id" not in item or "status" not in item:
                    continue

                attendance = {
                    "external_id": str(uuid.uuid4()),
                    "participant_external_id": item["participant_external_id"],
                    "schedule_external_id": schedule_external_id,
                    "date": attendance_date,
                    "status": item["status"]
                }
                records.append(attendance)
                created_records.append(attendance)

            self._save(records)

            return success_response(
                msg=f"Se registraron {len(created_records)} asistencias (MOCK)",
                data={"total": len(created_records), "attendances": created_records}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_attendances(self, filters=None):
        """Obtener todas las asistencias con filtros opcionales"""
        try:
            records = self._load()

            if filters:
                if filters.get("participant_external_id"):
                    records = [r for r in records if r.get("participant_external_id") == filters["participant_external_id"]]
                if filters.get("schedule_external_id"):
                    records = [r for r in records if r.get("schedule_external_id") == filters["schedule_external_id"]]
                if filters.get("date"):
                    records = [r for r in records if r.get("date") == filters["date"]]
                if filters.get("status"):
                    records = [r for r in records if r.get("status") == filters["status"]]

            return success_response(
                msg="Asistencias obtenidas correctamente (MOCK)",
                data=records
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_attendance_by_id(self, external_id):
        """Obtener una asistencia específica por su external_id"""
        try:
            records = self._load()
            attendance = next((r for r in records if r.get("external_id") == external_id), None)

            if not attendance:
                return error_response("Asistencia no encontrada", code=404)

            return success_response(
                msg="Asistencia encontrada (MOCK)",
                data=attendance
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def update_attendance(self, external_id, data):
        """Actualizar una asistencia existente"""
        try:
            records = self._load()
            index = next((i for i, r in enumerate(records) if r.get("external_id") == external_id), None)

            if index is None:
                return error_response("Asistencia no encontrada", code=404)

            if "status" in data:
                if data["status"] not in ["present", "absent"]:
                    return error_response("Estado inválido. Use: present, absent")
                records[index]["status"] = data["status"]

            self._save(records)

            return success_response(
                msg="Asistencia actualizada correctamente (MOCK)",
                data=records[index]
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def delete_attendance(self, external_id):
        """Eliminar una asistencia"""
        try:
            records = self._load()
            index = next((i for i, r in enumerate(records) if r.get("external_id") == external_id), None)

            if index is None:
                return error_response("Asistencia no encontrada", code=404)

            deleted = records.pop(index)
            self._save(records)

            return success_response(
                msg="Asistencia eliminada correctamente (MOCK)",
                data=deleted
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_participant_summary(self, participant_external_id):
        """Obtener resumen de asistencias de un participante"""
        try:
            records = self._load()
            attendances = [r for r in records if r.get("participant_external_id") == participant_external_id]

            total = len(attendances)
            present_count = len([a for a in attendances if a.get("status") == "present"])
            absent_count = len([a for a in attendances if a.get("status") == "absent"])
            percentage = round((present_count / total * 100), 2) if total > 0 else 0

            return success_response(
                msg="Resumen obtenido correctamente (MOCK)",
                data={
                    "participant_external_id": participant_external_id,
                    "total_sessions": total,
                    "present": present_count,
                    "absent": absent_count,
                    "attendance_percentage": percentage
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")



    def get_participants(self, program=None):
        """Obtener todos los participantes (MOCK)"""
        try:
            participants = self._load(self.participants_path)
            
            if program:
                participants = [p for p in participants if str(p.get("program_id", "")) == str(program) or p.get("program_name") == program or p.get("program") == program]

            return success_response(
                msg="Participantes obtenidos correctamente (MOCK)",
                data=participants
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_schedules(self):
        """Obtener todos los horarios/schedules (MOCK)"""
        try:
            schedules = self._load(self.schedules_path)
            return success_response(
                msg="Horarios obtenidos correctamente (MOCK)",
                data=schedules
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_today_sessions(self):
        """Obtener las sesiones programadas para hoy (MOCK)"""
        try:
            schedules = self._load(self.schedules_path)
            records = self._load()
            participants = self._load(self.participants_path)
            today = date.today().isoformat()
            
            weekdays_en = {
                0: "monday", 1: "tuesday", 2: "wednesday", 
                3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"
            }
            weekdays_es = {
                0: "Lunes", 1: "Martes", 2: "Miércoles", 
                3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
            }
            today_weekday_en = weekdays_en.get(date.today().weekday(), "")
            today_weekday_es = weekdays_es.get(date.today().weekday(), "")
            
            today_sessions = []
            for s in schedules:
                is_today = False
                
                specific_date = s.get("specific_date") or s.get("fecha_especifica")
                if specific_date:
                    is_today = (specific_date == today)
                else:
                    day = (s.get("dayOfWeek") or s.get("day_of_week") or "").lower()
                    if day == today_weekday_en:
                        start_date = s.get("start_date")
                        end_date = s.get("end_date")
                        if start_date and end_date:
                            is_today = (start_date <= today <= end_date)
                        elif start_date:
                            is_today = (today >= start_date)
                        elif end_date:
                            is_today = (today <= end_date)
                        else:
                            is_today = True
                
                if is_today:
                    schedule_id = s.get("external_id")
                    session_attendances = [r for r in records 
                                         if r.get("schedule_external_id") == schedule_id and r.get("date") == today]
                    present_count = len([a for a in session_attendances if a.get("status") == "present"])
                    
                    session = {
                        "id": s.get("id", 0),
                        "schedule_id": schedule_id,
                        "external_id": schedule_id,
                        "name": s.get("name", ""),
                        "start_time": s.get("startTime") or s.get("start_time", ""),
                        "end_time": s.get("endTime") or s.get("end_time", ""),
                        "program_name": s.get("program_name", ""),
                        "location": s.get("location", ""),
                        "attendance_count": present_count,
                        "participant_count": len(participants),
                        "specific_date": specific_date,
                        "is_recurring": s.get("is_recurring", True)
                    }
                    today_sessions.append(session)
            
            return success_response(
                msg="Sesiones de hoy obtenidas correctamente (MOCK)",
                data={
                    "date": today,
                    "day": today_weekday_es,
                    "sessions": today_sessions
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_history(self, date_from=None, date_to=None, schedule_id=None, day_filter=None):
        """Obtener historial de asistencias con rango de fechas (MOCK)"""
        try:
            records = self._load()
            participants = self._load(self.participants_path)
            schedules = self._load(self.schedules_path)
            
            participants_dict = {p.get("external_id"): p for p in participants}
            schedules_dict = {s.get("external_id"): s for s in schedules}
            
            if date_from:
                records = [r for r in records if r.get("date", "") >= date_from]
            if date_to:
                records = [r for r in records if r.get("date", "") <= date_to]
            
            if schedule_id:
                records = [r for r in records if r.get("schedule_external_id") == schedule_id]
            
            if day_filter and day_filter.lower() != "todos los días":
                day_map_es_to_en = {
                    'lunes': 'monday', 'martes': 'tuesday', 'miércoles': 'wednesday',
                    'miercoles': 'wednesday', 'jueves': 'thursday', 'viernes': 'friday',
                    'sábado': 'saturday', 'sabado': 'saturday', 'domingo': 'sunday'
                }
                day_en = day_map_es_to_en.get(day_filter.lower(), day_filter.lower())
                
                filtered_records = []
                for r in records:
                    schedule = schedules_dict.get(r.get("schedule_external_id"), {})
                    schedule_day = (schedule.get("day_of_week") or schedule.get("dayOfWeek") or "").lower()
                    if schedule_day == day_en:
                        filtered_records.append(r)
                records = filtered_records
            
            grouped = {}
            for r in records:
                key = f"{r.get('schedule_external_id')}_{r.get('date')}"
                if key not in grouped:
                    schedule = schedules_dict.get(r.get("schedule_external_id"), {})
                    grouped[key] = {
                        "schedule_id": r.get("schedule_external_id"),
                        "schedule_name": schedule.get("name", ""),
                        "date": r.get("date"),
                        "day_of_week": schedule.get("day_of_week") or schedule.get("dayOfWeek", ""),
                        "start_time": schedule.get("startTime") or schedule.get("start_time", ""),
                        "end_time": schedule.get("endTime") or schedule.get("end_time", ""),
                        "presentes": 0,
                        "ausentes": 0,
                        "total": 0
                    }
                
                grouped[key]["total"] += 1
                if r.get("status") == "present":
                    grouped[key]["presentes"] += 1
                else:
                    grouped[key]["ausentes"] += 1
            
            history = list(grouped.values())
            history.sort(key=lambda x: x.get("date", ""), reverse=True)
            
            return success_response(
                msg="Historial obtenido correctamente (MOCK)",
                data=history
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def _calculate_date_for_weekday(self, day_of_week):
        """Calcular la fecha correspondiente al día de la semana del schedule"""
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_day = day_map.get(day_of_week.lower() if day_of_week else None)
        if target_day is None:
            return date.today().isoformat()
        
        today = date.today()
        current_day = today.weekday()
        
        diff = target_day - current_day
        if diff > 0:
            diff -= 7
        
        target_date = today + timedelta(days=diff)
        return target_date.isoformat()

    def register_public_attendance(self, data):
        """Registrar asistencia desde el frontend (MOCK)"""
        try:
            if not data:
                return error_response("No se enviaron datos")
            
            schedule_id = data.get("schedule_id") or data.get("schedule_external_id")
            
            schedules = self._load(self.schedules_path)
            schedule = next((s for s in schedules if str(s.get("external_id")) == str(schedule_id)), None)
            
            day_of_week = schedule.get("dayOfWeek") or schedule.get("day_of_week") if schedule else None
            if day_of_week:
                attendance_date = self._calculate_date_for_weekday(day_of_week)
            else:
                attendance_date = data.get("date", date.today().isoformat())
            
            attendances = data.get("attendance", {})
            input_records = data.get("records", [])
            input_attendances = data.get("attendances", [])
            
            if input_attendances and isinstance(input_attendances, list):
                attendances = {}
                for r in input_attendances:
                    pid = str(r.get("participant_external_id", "") or r.get("participant_id", ""))
                    status = r.get("status", "PRESENT")
                    if pid:
                        attendances[pid] = status
            
            if input_records and isinstance(input_records, list):
                attendances = {}
                for r in input_records:
                    pid = str(r.get("participant_id", "") or r.get("participant_external_id", ""))
                    status = r.get("status", "PRESENT")
                    if pid:
                        attendances[pid] = status
            
            # Convertir schedule_id a string si viene como int
            schedule_id = str(schedule_id) if schedule_id else None
            
            if not schedule_id:
                return error_response("Falta el campo: schedule_id")
            if not attendances:
                return error_response("Falta el campo: attendance, records o attendances")
            
            records = self._load()
            new_records = []
            
            for participant_id, status in attendances.items():
                participant_id = str(participant_id)
                exists = False
                for r in records:
                    r_pid = str(r.get("participant_external_id", ""))
                    r_sid = str(r.get("schedule_external_id", ""))
                    if (r_pid == participant_id and 
                        r_sid == schedule_id and 
                        r.get("date") == attendance_date):
                        r["status"] = status.lower() if isinstance(status, str) else status
                        exists = True
                        break
                
                if not exists:
                    new_record = {
                        "external_id": str(uuid.uuid4()),
                        "participant_external_id": participant_id,
                        "schedule_external_id": schedule_id,
                        "date": attendance_date,
                        "status": status.lower() if isinstance(status, str) else status
                    }
                    records.append(new_record)
                    new_records.append(new_record)
            
            self._save(records)
            
            return success_response(
                msg=f"Asistencia registrada correctamente (MOCK)",
                data={"total": len(attendances), "date": attendance_date, "schedule_id": schedule_id}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_programs(self):
        """Obtener todos los programas (MOCK)"""
        try:
            schedules = self._load(self.schedules_path)
            programs = {}
            for s in schedules:
                pid = s.get("program_id")
                if pid and pid not in programs:
                    programs[pid] = {
                        "id": pid,
                        "name": s.get("program_name", f"Programa {pid}"),
                        "external_id": f"prog-{pid}-uuid"
                    }
            
            return success_response(
                msg="Programas obtenidos correctamente (MOCK)",
                data=list(programs.values())
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def get_session_detail(self, schedule_id, attendance_date):
        """Obtener detalle de asistencia de una sesión específica (MOCK)"""
        try:
            records = self._load()
            participants = self._load(self.participants_path)
            schedules = self._load(self.schedules_path)
            
            schedule = next((s for s in schedules if s.get("external_id") == schedule_id), None)
            
            session_attendances = [r for r in records 
                         if r.get("schedule_external_id") == schedule_id and r.get("date") == attendance_date]
            
            participants_dict = {p.get("external_id"): p for p in participants}
            for i, p in enumerate(participants, start=1):
                participants_dict[str(i)] = p
            
            detail_records = []
            for a in session_attendances:
                participant_id = a.get("participant_external_id")
                participant = participants_dict.get(participant_id, {})
                
                first_name = participant.get('firstName') or participant.get('first_name', '')
                last_name = participant.get('lastName') or participant.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()
                
                detail_records.append({
                    "external_id": a.get("external_id"),
                    "participant_id": participant_id,
                    "participant_name": full_name if full_name else f"Participante {participant_id}",
                    "dni": participant.get("dni", ""),
                    "status": a.get("status", "").upper()
                })
            
            present_count = len([r for r in detail_records if r.get("status") == "PRESENT"])
            absent_count = len([r for r in detail_records if r.get("status") in ["ABSENT", "JUSTIFIED"]])
            total = len(detail_records)
            
            return success_response(
                msg="Detalle de sesión obtenido correctamente (MOCK)",
                data={
                    "schedule_id": schedule_id,
                    "date": attendance_date,
                    "schedule": schedule,
                    "records": detail_records,
                    "stats": {
                        "presentes": present_count,
                        "ausentes": absent_count,
                        "total": total
                    },
                    "total": total,
                    "present": present_count,
                    "absent": absent_count
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def delete_session_attendance(self, schedule_id, attendance_date):
        """Eliminar asistencia de una sesión específica (MOCK)"""
        try:
            records = self._load()
            
            filtered_records = [r for r in records 
                                  if not (r.get("schedule_external_id") == schedule_id and r.get("date") == attendance_date)]
            
            deleted_count = len(records) - len(filtered_records)
            
            if deleted_count == 0:
                return error_response("No se encontraron registros para eliminar", code=404)
            
            self._save(filtered_records)
            
            return success_response(
                msg=f"Se eliminaron {deleted_count} registros de asistencia (MOCK)",
                data={"deleted": deleted_count, "schedule_id": schedule_id, "date": attendance_date}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def create_schedule(self, data):
        """Crear un nuevo horario/sesión (MOCK)"""
        try:
            if not data:
                return error_response("No se enviaron datos")
            
            name = data.get("name") or data.get("nombre")
            day = data.get("day_of_week") or data.get("dia")
            start_time = data.get("start_time") or data.get("hora_inicio")
            end_time = data.get("end_time") or data.get("hora_fin")
            location = data.get("location") or data.get("ubicacion", "")
            capacity = data.get("capacity") or data.get("capacidad", 30)
            description = data.get("description") or data.get("descripcion", "")
            program_id = data.get("program_id", 1)
            
            start_date = data.get("start_date") or data.get("fecha_inicio")
            end_date = data.get("end_date") or data.get("fecha_fin")
            specific_date = data.get("specific_date") or data.get("fecha_especifica")
            is_recurring = data.get("is_recurring", True)
            
            if not name:
                return error_response("Falta el campo: name/nombre")
            if not day and not specific_date:
                return error_response("Falta el campo: day_of_week/dia o specific_date/fecha_especifica")
            if not start_time:
                return error_response("Falta el campo: start_time/hora_inicio")
            if not end_time:
                return error_response("Falta el campo: end_time/hora_fin")
            
            if specific_date:
                from datetime import datetime
                try:
                    specific_date_obj = datetime.strptime(specific_date, "%Y-%m-%d")
                    weekdays_en = {
                        0: "monday", 1: "tuesday", 2: "wednesday", 
                        3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"
                    }
                    day = weekdays_en.get(specific_date_obj.weekday(), "monday")
                    is_recurring = False
                except ValueError:
                    return error_response("Formato de fecha inválido. Use: YYYY-MM-DD")
            
            day_map = {
                'lunes': 'monday', 'martes': 'tuesday', 'miercoles': 'wednesday',
                'miércoles': 'wednesday', 'jueves': 'thursday', 'viernes': 'friday',
                'sabado': 'saturday', 'sábado': 'saturday', 'domingo': 'sunday'
            }
            day_lower = day.lower() if day else ""
            day_en = day_map.get(day_lower, day_lower)
            
            schedules = self._load(self.schedules_path)
            
            new_schedule = {
                "external_id": str(uuid.uuid4()),
                "program_id": program_id,
                "program_name": "Iniciación" if program_id == 2 else "Funcional",
                "day_of_week": day_en,
                "start_time": start_time,
                "end_time": end_time,
                "name": name,
                "location": location,
                "capacity": capacity,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "specific_date": specific_date,
                "is_recurring": is_recurring
            }
            
            schedules.append(new_schedule)
            self._save(schedules, self.schedules_path)
            
            return success_response(
                msg="Sesión creada correctamente (MOCK)",
                data=new_schedule
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def update_schedule(self, schedule_id, data):
        """Actualizar un horario/sesión (MOCK)"""
        try:
            if not data:
                return error_response("No se enviaron datos")
            
            schedules = self._load(self.schedules_path)
            
            # Buscar el schedule
            found_schedule = None
            for s in schedules:
                if s.get("external_id") == schedule_id:
                    found_schedule = s
                    break
            
            if not found_schedule:
                return error_response("Sesión no encontrada", code=404)
            
            # Mapear día a inglés si viene en español
            day_map = {
                'lunes': 'monday', 'martes': 'tuesday', 'miercoles': 'wednesday',
                'miércoles': 'wednesday', 'jueves': 'thursday', 'viernes': 'friday',
                'sabado': 'saturday', 'sábado': 'saturday', 'domingo': 'sunday'
            }
            
            # Actualizar campos si vienen en data
            if data.get("name") or data.get("nombre"):
                found_schedule["name"] = data.get("name") or data.get("nombre")
            if data.get("day_of_week") or data.get("dia"):
                day = data.get("day_of_week") or data.get("dia")
                found_schedule["day_of_week"] = day_map.get(day.lower(), day.lower())
            if data.get("start_time") or data.get("hora_inicio"):
                found_schedule["start_time"] = data.get("start_time") or data.get("hora_inicio")
            if data.get("end_time") or data.get("hora_fin"):
                found_schedule["end_time"] = data.get("end_time") or data.get("hora_fin")
            if data.get("location") or data.get("ubicacion"):
                found_schedule["location"] = data.get("location") or data.get("ubicacion")
            if data.get("capacity") or data.get("capacidad"):
                found_schedule["capacity"] = data.get("capacity") or data.get("capacidad")
            if data.get("description") or data.get("descripcion"):
                found_schedule["description"] = data.get("description") or data.get("descripcion")
            
            # Nuevos campos de fecha
            if data.get("start_date") or data.get("fecha_inicio"):
                found_schedule["start_date"] = data.get("start_date") or data.get("fecha_inicio")
            if data.get("end_date") or data.get("fecha_fin"):
                found_schedule["end_date"] = data.get("end_date") or data.get("fecha_fin")
            if data.get("specific_date") or data.get("fecha_especifica"):
                specific_date = data.get("specific_date") or data.get("fecha_especifica")
                found_schedule["specific_date"] = specific_date
                # Derivar día de la semana de la fecha específica
                from datetime import datetime
                try:
                    specific_date_obj = datetime.strptime(specific_date, "%Y-%m-%d")
                    weekdays_en = {
                        0: "monday", 1: "tuesday", 2: "wednesday", 
                        3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"
                    }
                    found_schedule["day_of_week"] = weekdays_en.get(specific_date_obj.weekday(), "monday")
                except ValueError:
                    pass
            if "is_recurring" in data:
                found_schedule["is_recurring"] = data.get("is_recurring")
            
            self._save(schedules, self.schedules_path)
            
            return success_response(
                msg="Sesión actualizada correctamente (MOCK)",
                data=found_schedule
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def delete_schedule(self, schedule_id):
        """Eliminar un horario/sesión (MOCK)"""
        try:
            schedules = self._load(self.schedules_path)
            
            # Buscar el schedule
            found_schedule = None
            filtered_schedules = []
            for s in schedules:
                if s.get("external_id") == schedule_id:
                    found_schedule = s
                else:
                    filtered_schedules.append(s)
            
            if not found_schedule:
                return error_response("Sesión no encontrada", code=404)
            
            self._save(filtered_schedules, self.schedules_path)
            
            return success_response(
                msg="Sesión eliminada correctamente (MOCK)",
                data={"deleted_id": schedule_id}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")
