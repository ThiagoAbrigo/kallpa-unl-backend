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

    def registrar_asistencia(self, data):
        """Registrar una asistencia individual"""
        if not data:
            return error_response("No se enviaron datos")

        campos = ["participant_external_id", "schedule_external_id", "status"]
        for campo in campos:
            if campo not in data:
                return error_response(f"Falta el campo requerido: {campo}")

        # Validar status
        valid_statuses = ["present", "absent"]
        if data["status"] not in valid_statuses:
            return error_response(f"Estado inválido. Use: {valid_statuses}")

        try:
            registros = self._load()

            attendance = {
                "external_id": str(uuid.uuid4()),
                "participant_external_id": data["participant_external_id"],
                "schedule_external_id": data["schedule_external_id"],
                "date": data.get("date", date.today().isoformat()),
                "status": data["status"]
            }

            registros.append(attendance)
            self._save(registros)

            return success_response(
                msg="Asistencia registrada correctamente (MOCK)",
                data=attendance
            )
        except Exception as e:
            return error_response(f"Error interno al guardar la asistencia: {e}")

    def registrar_asistencia_masiva(self, data):
        """Registrar múltiples asistencias de una sesión"""
        if not data:
            return error_response("No se enviaron datos")

        if "schedule_external_id" not in data:
            return error_response("Falta el campo: schedule_external_id")
        
        if "attendances" not in data or not isinstance(data["attendances"], list):
            return error_response("Falta el campo: attendances (debe ser una lista)")

        try:
            registros = self._load()
            fecha = data.get("date", date.today().isoformat())
            schedule_external_id = data["schedule_external_id"]
            
            registros_creados = []

            for item in data["attendances"]:
                if "participant_external_id" not in item or "status" not in item:
                    continue

                attendance = {
                    "external_id": str(uuid.uuid4()),
                    "participant_external_id": item["participant_external_id"],
                    "schedule_external_id": schedule_external_id,
                    "date": fecha,
                    "status": item["status"]
                }
                registros.append(attendance)
                registros_creados.append(attendance)

            self._save(registros)

            return success_response(
                msg=f"Se registraron {len(registros_creados)} asistencias (MOCK)",
                data={"total": len(registros_creados), "attendances": registros_creados}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_asistencias(self, filters=None):
        """Obtener todas las asistencias con filtros opcionales"""
        try:
            registros = self._load()

            if filters:
                if filters.get("participant_external_id"):
                    registros = [r for r in registros if r.get("participant_external_id") == filters["participant_external_id"]]
                if filters.get("schedule_external_id"):
                    registros = [r for r in registros if r.get("schedule_external_id") == filters["schedule_external_id"]]
                if filters.get("date"):
                    registros = [r for r in registros if r.get("date") == filters["date"]]
                if filters.get("status"):
                    registros = [r for r in registros if r.get("status") == filters["status"]]

            return success_response(
                msg="Asistencias obtenidas correctamente (MOCK)",
                data=registros
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_asistencia_por_id(self, external_id):
        """Obtener una asistencia específica por su external_id"""
        try:
            registros = self._load()
            attendance = next((r for r in registros if r.get("external_id") == external_id), None)

            if not attendance:
                return error_response("Asistencia no encontrada", code=404)

            return success_response(
                msg="Asistencia encontrada (MOCK)",
                data=attendance
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def actualizar_asistencia(self, external_id, data):
        """Actualizar una asistencia existente"""
        try:
            registros = self._load()
            index = next((i for i, r in enumerate(registros) if r.get("external_id") == external_id), None)

            if index is None:
                return error_response("Asistencia no encontrada", code=404)

            # Actualizar campos permitidos
            if "status" in data:
                if data["status"] not in ["present", "absent"]:
                    return error_response("Estado inválido. Use: present, absent")
                registros[index]["status"] = data["status"]

            self._save(registros)

            return success_response(
                msg="Asistencia actualizada correctamente (MOCK)",
                data=registros[index]
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def eliminar_asistencia(self, external_id):
        """Eliminar una asistencia"""
        try:
            registros = self._load()
            index = next((i for i, r in enumerate(registros) if r.get("external_id") == external_id), None)

            if index is None:
                return error_response("Asistencia no encontrada", code=404)

            eliminado = registros.pop(index)
            self._save(registros)

            return success_response(
                msg="Asistencia eliminada correctamente (MOCK)",
                data=eliminado
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_resumen_por_participante(self, participant_external_id):
        """Obtener resumen de asistencias de un participante"""
        try:
            registros = self._load()
            asistencias = [r for r in registros if r.get("participant_external_id") == participant_external_id]

            total = len(asistencias)
            presentes = len([a for a in asistencias if a.get("status") == "present"])
            ausentes = len([a for a in asistencias if a.get("status") == "absent"])
            porcentaje = round((presentes / total * 100), 2) if total > 0 else 0

            return success_response(
                msg="Resumen obtenido correctamente (MOCK)",
                data={
                    "participant_external_id": participant_external_id,
                    "total_sessions": total,
                    "present": presentes,
                    "absent": ausentes,
                    "attendance_percentage": porcentaje
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    # ==================== MÉTODOS PÚBLICOS PARA EL FRONTEND ====================

    def obtener_participantes(self):
        """Obtener todos los participantes (MOCK)"""
        try:
            participants = self._load(self.participants_path)
            return success_response(
                msg="Participantes obtenidos correctamente (MOCK)",
                data=participants
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_schedules(self):
        """Obtener todos los horarios/schedules (MOCK)"""
        try:
            schedules = self._load(self.schedules_path)
            return success_response(
                msg="Horarios obtenidos correctamente (MOCK)",
                data=schedules
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_sesiones_hoy(self):
        """Obtener las sesiones programadas para hoy (MOCK)"""
        try:
            schedules = self._load(self.schedules_path)
            registros = self._load()
            participants = self._load(self.participants_path)
            hoy = date.today().isoformat()
            
            # Mapear día de la semana
            dias_semana = {
                0: "monday", 1: "tuesday", 2: "wednesday", 
                3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"
            }
            dias_semana_es = {
                0: "Lunes", 1: "Martes", 2: "Miércoles", 
                3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
            }
            dia_hoy_en = dias_semana.get(date.today().weekday(), "")
            dia_hoy_es = dias_semana_es.get(date.today().weekday(), "")
            
            # Filtrar schedules del día de hoy
            sesiones_hoy = []
            for s in schedules:
                day = (s.get("dayOfWeek") or s.get("day_of_week") or "").lower()
                if day == dia_hoy_en:
                    # Contar asistencias de esta sesión para hoy
                    schedule_id = s.get("external_id")
                    asistencias_sesion = [r for r in registros 
                                         if r.get("schedule_external_id") == schedule_id and r.get("date") == hoy]
                    presentes = len([a for a in asistencias_sesion if a.get("status") == "present"])
                    
                    sesion = {
                        "id": s.get("id", 0),
                        "schedule_id": schedule_id,
                        "external_id": schedule_id,
                        "name": s.get("name", ""),
                        "start_time": s.get("startTime") or s.get("start_time", ""),
                        "end_time": s.get("endTime") or s.get("end_time", ""),
                        "program_name": s.get("program_name", ""),
                        "location": s.get("location", ""),
                        "attendance_count": presentes,
                        "participant_count": len(participants)  # Total de participantes
                    }
                    sesiones_hoy.append(sesion)
            
            return success_response(
                msg="Sesiones de hoy obtenidas correctamente (MOCK)",
                data={
                    "date": hoy,
                    "day": dia_hoy_es,
                    "sessions": sesiones_hoy
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_historial(self, date_from=None, date_to=None, schedule_id=None):
        """Obtener historial de asistencias con rango de fechas (MOCK)"""
        try:
            registros = self._load()
            participants = self._load(self.participants_path)
            schedules = self._load(self.schedules_path)
            
            # Crear diccionarios para lookup rápido
            participants_dict = {p.get("external_id"): p for p in participants}
            schedules_dict = {s.get("external_id"): s for s in schedules}
            
            # Filtrar por rango de fechas si se proporciona
            if date_from:
                registros = [r for r in registros if r.get("date", "") >= date_from]
            if date_to:
                registros = [r for r in registros if r.get("date", "") <= date_to]
            
            # Filtrar por schedule_id si se proporciona
            if schedule_id:
                registros = [r for r in registros if r.get("schedule_external_id") == schedule_id]
            
            # Agrupar por schedule_id y fecha para el formato esperado por el frontend
            agrupado = {}
            for r in registros:
                key = f"{r.get('schedule_external_id')}_{r.get('date')}"
                if key not in agrupado:
                    schedule = schedules_dict.get(r.get("schedule_external_id"), {})
                    agrupado[key] = {
                        "schedule_id": r.get("schedule_external_id"),
                        "schedule_name": schedule.get("name", ""),
                        "date": r.get("date"),
                        "start_time": schedule.get("startTime") or schedule.get("start_time", ""),
                        "end_time": schedule.get("endTime") or schedule.get("end_time", ""),
                        "presentes": 0,
                        "ausentes": 0,
                        "total": 0
                    }
                
                agrupado[key]["total"] += 1
                if r.get("status") == "present":
                    agrupado[key]["presentes"] += 1
                else:
                    agrupado[key]["ausentes"] += 1
            
            historial = list(agrupado.values())
            # Ordenar por fecha descendente
            historial.sort(key=lambda x: x.get("date", ""), reverse=True)
            
            return success_response(
                msg="Historial obtenido correctamente (MOCK)",
                data=historial
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def _calcular_fecha_para_dia_semana(self, day_of_week):
        """Calcular la fecha correspondiente al día de la semana del schedule"""
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_day = day_map.get(day_of_week.lower() if day_of_week else None)
        if target_day is None:
            return date.today().isoformat()
        
        today = date.today()
        current_day = today.weekday()  # 0=lunes, 1=martes, etc.
        
        # Calcular diferencia de días (buscamos el día más reciente, incluyendo hoy)
        diff = target_day - current_day
        if diff > 0:
            # El día está adelante en la semana, ir a la semana anterior
            diff -= 7
        
        target_date = today + timedelta(days=diff)
        return target_date.isoformat()

    def registrar_asistencia_publica(self, data):
        """Registrar asistencia desde el frontend (MOCK)"""
        try:
            if not data:
                return error_response("No se enviaron datos")
            
            schedule_id = data.get("schedule_id")
            
            # Obtener el schedule para conocer el día de la semana
            schedules = self._load(self.schedules_path)
            schedule = next((s for s in schedules if str(s.get("external_id")) == str(schedule_id)), None)
            
            # Calcular la fecha basándose en el día de la semana del schedule
            day_of_week = schedule.get("dayOfWeek") or schedule.get("day_of_week") if schedule else None
            if day_of_week:
                fecha = self._calcular_fecha_para_dia_semana(day_of_week)
            else:
                fecha = data.get("date", date.today().isoformat())
            
            # Soportar ambos formatos: 
            # - attendance: {participant_id: status} (diccionario)
            # - records: [{participant_id, status}] (array)
            attendances = data.get("attendance", {})
            records = data.get("records", [])
            
            # Convertir records a formato attendances si viene como array
            if records and isinstance(records, list):
                attendances = {}
                for r in records:
                    pid = str(r.get("participant_id", ""))
                    status = r.get("status", "PRESENT")
                    attendances[pid] = status
            
            # Convertir schedule_id a string si viene como int
            schedule_id = str(schedule_id) if schedule_id else None
            
            if not schedule_id:
                return error_response("Falta el campo: schedule_id")
            if not attendances:
                return error_response("Falta el campo: attendance o records")
            
            registros = self._load()
            nuevos_registros = []
            
            for participant_id, status in attendances.items():
                participant_id = str(participant_id)  # Asegurar string
                # Buscar si ya existe un registro para este participante/sesión/fecha
                existe = False
                for r in registros:
                    r_pid = str(r.get("participant_external_id", ""))
                    r_sid = str(r.get("schedule_external_id", ""))
                    if (r_pid == participant_id and 
                        r_sid == schedule_id and 
                        r.get("date") == fecha):
                        # Actualizar existente
                        r["status"] = status.lower() if isinstance(status, str) else status
                        existe = True
                        break
                
                if not existe:
                    nuevo = {
                        "external_id": str(uuid.uuid4()),
                        "participant_external_id": participant_id,
                        "schedule_external_id": schedule_id,
                        "date": fecha,
                        "status": status.lower() if isinstance(status, str) else status
                    }
                    registros.append(nuevo)
                    nuevos_registros.append(nuevo)
            
            self._save(registros)
            
            return success_response(
                msg=f"Asistencia registrada correctamente (MOCK)",
                data={"total": len(attendances), "date": fecha, "schedule_id": schedule_id}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_programas(self):
        """Obtener todos los programas (MOCK)"""
        try:
            # Extraer programas únicos de los schedules
            schedules = self._load(self.schedules_path)
            programas = {}
            for s in schedules:
                pid = s.get("program_id")
                if pid and pid not in programas:
                    programas[pid] = {
                        "id": pid,
                        "name": s.get("program_name", f"Programa {pid}"),
                        "external_id": f"prog-{pid}-uuid"
                    }
            
            return success_response(
                msg="Programas obtenidos correctamente (MOCK)",
                data=list(programas.values())
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def obtener_detalle_sesion(self, schedule_id, fecha):
        """Obtener detalle de asistencia de una sesión específica (MOCK)"""
        try:
            registros = self._load()
            participants = self._load(self.participants_path)
            schedules = self._load(self.schedules_path)
            
            # Buscar el schedule
            schedule = next((s for s in schedules if s.get("external_id") == schedule_id), None)
            
            # Filtrar asistencias de esta sesión y fecha
            asistencias = [r for r in registros 
                         if r.get("schedule_external_id") == schedule_id and r.get("date") == fecha]
            
            # Crear diccionarios de participantes (por external_id y por índice numérico)
            participants_dict = {p.get("external_id"): p for p in participants}
            # También indexar por número (1, 2, 3...) para compatibilidad con datos antiguos
            for i, p in enumerate(participants, start=1):
                participants_dict[str(i)] = p
            
            records = []
            for a in asistencias:
                participant_id = a.get("participant_external_id")
                participant = participants_dict.get(participant_id, {})
                
                # Obtener nombre del participante (soportar firstName/lastName o first_name/last_name)
                first_name = participant.get('firstName') or participant.get('first_name', '')
                last_name = participant.get('lastName') or participant.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()
                
                records.append({
                    "external_id": a.get("external_id"),
                    "participant_id": participant_id,
                    "participant_name": full_name if full_name else f"Participante {participant_id}",
                    "dni": participant.get("dni", ""),
                    "status": a.get("status", "").upper()
                })
            
            # Calcular estadísticas
            presentes = len([r for r in records if r.get("status") == "PRESENT"])
            ausentes = len([r for r in records if r.get("status") in ["ABSENT", "JUSTIFIED"]])
            total = len(records)
            
            return success_response(
                msg="Detalle de sesión obtenido correctamente (MOCK)",
                data={
                    "schedule_id": schedule_id,
                    "date": fecha,
                    "schedule": schedule,
                    "records": records,
                    "stats": {
                        "presentes": presentes,
                        "ausentes": ausentes,
                        "total": total
                    },
                    "total": total,
                    "present": presentes,
                    "absent": ausentes
                }
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def eliminar_asistencia_sesion(self, schedule_id, fecha):
        """Eliminar asistencia de una sesión específica (MOCK)"""
        try:
            registros = self._load()
            
            # Filtrar los registros que NO son de esta sesión/fecha (quedarse con los demás)
            registros_filtrados = [r for r in registros 
                                  if not (r.get("schedule_external_id") == schedule_id and r.get("date") == fecha)]
            
            eliminados = len(registros) - len(registros_filtrados)
            
            if eliminados == 0:
                return error_response("No se encontraron registros para eliminar", code=404)
            
            self._save(registros_filtrados)
            
            return success_response(
                msg=f"Se eliminaron {eliminados} registros de asistencia (MOCK)",
                data={"deleted": eliminados, "schedule_id": schedule_id, "date": fecha}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def crear_schedule(self, data):
        """Crear un nuevo horario/sesión (MOCK)"""
        try:
            if not data:
                return error_response("No se enviaron datos")
            
            nombre = data.get("name") or data.get("nombre")
            dia = data.get("day_of_week") or data.get("dia")
            hora_inicio = data.get("start_time") or data.get("hora_inicio")
            hora_fin = data.get("end_time") or data.get("hora_fin")
            ubicacion = data.get("location") or data.get("ubicacion", "")
            capacidad = data.get("capacity") or data.get("capacidad", 30)
            descripcion = data.get("description") or data.get("descripcion", "")
            program_id = data.get("program_id", 1)
            
            if not nombre:
                return error_response("Falta el campo: name/nombre")
            if not dia:
                return error_response("Falta el campo: day_of_week/dia")
            if not hora_inicio:
                return error_response("Falta el campo: start_time/hora_inicio")
            if not hora_fin:
                return error_response("Falta el campo: end_time/hora_fin")
            
            # Mapear día a inglés si viene en español
            day_map = {
                'lunes': 'monday', 'martes': 'tuesday', 'miercoles': 'wednesday',
                'miércoles': 'wednesday', 'jueves': 'thursday', 'viernes': 'friday',
                'sabado': 'saturday', 'sábado': 'saturday', 'domingo': 'sunday'
            }
            dia_lower = dia.lower()
            dia_en = day_map.get(dia_lower, dia_lower)
            
            schedules = self._load(self.schedules_path)
            
            nuevo_schedule = {
                "external_id": str(uuid.uuid4()),
                "program_id": program_id,
                "program_name": f"Programa {program_id}",
                "day_of_week": dia_en,
                "start_time": hora_inicio,
                "end_time": hora_fin,
                "name": nombre,
                "location": ubicacion,
                "capacity": capacidad,
                "description": descripcion
            }
            
            schedules.append(nuevo_schedule)
            self._save(schedules, self.schedules_path)
            
            return success_response(
                msg="Sesión creada correctamente (MOCK)",
                data=nuevo_schedule
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def actualizar_schedule(self, schedule_id, data):
        """Actualizar un horario/sesión (MOCK)"""
        try:
            if not data:
                return error_response("No se enviaron datos")
            
            schedules = self._load(self.schedules_path)
            
            # Buscar el schedule
            schedule_encontrado = None
            for s in schedules:
                if s.get("external_id") == schedule_id:
                    schedule_encontrado = s
                    break
            
            if not schedule_encontrado:
                return error_response("Sesión no encontrada", code=404)
            
            # Mapear día a inglés si viene en español
            day_map = {
                'lunes': 'monday', 'martes': 'tuesday', 'miercoles': 'wednesday',
                'miércoles': 'wednesday', 'jueves': 'thursday', 'viernes': 'friday',
                'sabado': 'saturday', 'sábado': 'saturday', 'domingo': 'sunday'
            }
            
            # Actualizar campos si vienen en data
            if data.get("name") or data.get("nombre"):
                schedule_encontrado["name"] = data.get("name") or data.get("nombre")
            if data.get("day_of_week") or data.get("dia"):
                dia = data.get("day_of_week") or data.get("dia")
                schedule_encontrado["day_of_week"] = day_map.get(dia.lower(), dia.lower())
            if data.get("start_time") or data.get("hora_inicio"):
                schedule_encontrado["start_time"] = data.get("start_time") or data.get("hora_inicio")
            if data.get("end_time") or data.get("hora_fin"):
                schedule_encontrado["end_time"] = data.get("end_time") or data.get("hora_fin")
            if data.get("location") or data.get("ubicacion"):
                schedule_encontrado["location"] = data.get("location") or data.get("ubicacion")
            if data.get("capacity") or data.get("capacidad"):
                schedule_encontrado["capacity"] = data.get("capacity") or data.get("capacidad")
            if data.get("description") or data.get("descripcion"):
                schedule_encontrado["description"] = data.get("description") or data.get("descripcion")
            
            self._save(schedules, self.schedules_path)
            
            return success_response(
                msg="Sesión actualizada correctamente (MOCK)",
                data=schedule_encontrado
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")

    def eliminar_schedule(self, schedule_id):
        """Eliminar un horario/sesión (MOCK)"""
        try:
            schedules = self._load(self.schedules_path)
            
            # Buscar el schedule
            schedule_encontrado = None
            schedules_filtrados = []
            for s in schedules:
                if s.get("external_id") == schedule_id:
                    schedule_encontrado = s
                else:
                    schedules_filtrados.append(s)
            
            if not schedule_encontrado:
                return error_response("Sesión no encontrada", code=404)
            
            self._save(schedules_filtrados, self.schedules_path)
            
            return success_response(
                msg="Sesión eliminada correctamente (MOCK)",
                data={"deleted_id": schedule_id}
            )
        except Exception as e:
            return error_response(f"Error interno: {e}")
