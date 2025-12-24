import json
import os
from app.utils.responses import success_response, error_response
import uuid
from datetime import date


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
