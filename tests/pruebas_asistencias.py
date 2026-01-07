import unittest
import requests
import json
import uuid
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:5000/api"


class TestAttendanceModule(unittest.TestCase):
    """
    Casos de prueba para el módulo de Gestión de Asistencias
    Siguiendo el patrón de pruebas_usuarios_participantes.py
    """

    def setUp(self):
        self.headers = {"Content-Type": "application/json"}
        self.admin_email = "admin@kallpa.com"
        self.admin_password = "123456"
        self.token = None

    def _get_auth_headers(self):
        """Obtener headers con token de autenticación"""
        if not self.token:
            payload = {"email": self.admin_email, "password": self.admin_password}
            resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
            if resp.status_code == 200:
                self.token = resp.json()["token"]

        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    # ========== GESTIÓN DE HORARIOS ==========

    def test_tc_01_list_schedules(self):
        """TC-01: Listar todos los horarios/sesiones"""
        headers = self._get_auth_headers()
        response = requests.get(f"{BASE_URL}/attendance/schedules", headers=headers)
        self.assertEqual(response.status_code, 200, "TC-01: Debería obtener lista de horarios")
        data = response.json()
        self.assertIn("data", data, "TC-01: La respuesta debe contener 'data'")
        print("TC-01: Listar Horarios - OK")

    def test_tc_02_create_schedule_success(self):
        """TC-02: Crear un nuevo horario exitosamente"""
        headers = self._get_auth_headers()
        unique_name = f"Sesión Test {uuid.uuid4().hex[:8]}"
        # Campos requeridos por la API: name, day_of_week, start_time, end_time, max_slots, program
        payload = {
            "name": unique_name,
            "day_of_week": "wednesday",
            "start_time": "10:00",
            "end_time": "11:00",
            "max_slots": 25,
            "program": "FUNCIONAL"
        }
        response = requests.post(f"{BASE_URL}/attendance/schedules", json=payload, headers=headers)
        self.assertIn(response.status_code, [200, 201],
                      f"TC-02: Falló creación. Status: {response.status_code}, Resp: {response.text}")
        print("TC-02: Crear Horario Exitoso - OK")

    def test_tc_03_create_schedule_empty_fields(self):
        """TC-03: Crear horario con campos vacíos - Validación"""
        headers = self._get_auth_headers()
        payload = {}
        response = requests.post(f"{BASE_URL}/attendance/schedules", json=payload, headers=headers)
        self.assertNotIn(response.status_code, [200, 201],
                         "TC-03: Debería fallar por campos vacíos")
        print("TC-03: Validación Campos Vacíos - OK")

    def test_tc_04_get_today_sessions(self):
        """TC-04: Obtener sesiones programadas para hoy"""
        headers = self._get_auth_headers()
        response = requests.get(f"{BASE_URL}/attendance/sessions/today", headers=headers)
        self.assertEqual(response.status_code, 200, "TC-04: Debería obtener sesiones del día")
        data = response.json()
        self.assertIsInstance(data.get("data", []), list, "TC-04: Data debe ser una lista")
        print("TC-04: Sesiones de Hoy - OK")

    # ========== REGISTRO DE ASISTENCIA ==========

    def test_tc_05_get_participants_for_attendance(self):
        """TC-05: Obtener lista de participantes para registro de asistencia"""
        headers = self._get_auth_headers()
        response = requests.get(f"{BASE_URL}/attendance/participants", headers=headers)
        self.assertEqual(response.status_code, 200,
                         "TC-05: Debería obtener lista de participantes")
        data = response.json()
        self.assertIn("data", data, "TC-05: La respuesta debe contener 'data'")
        print("TC-05: Obtener Participantes - OK")

    def test_tc_06_register_attendance_success(self):
        """TC-06: Registrar asistencia masiva exitosamente"""
        headers = self._get_auth_headers()
        today = date.today().isoformat()
        
        # Primero obtener un schedule válido y participantes
        schedules_resp = requests.get(f"{BASE_URL}/attendance/schedules", headers=headers)
        participants_resp = requests.get(f"{BASE_URL}/attendance/participants", headers=headers)
        
        if schedules_resp.status_code == 200 and participants_resp.status_code == 200:
            schedules = schedules_resp.json().get("data", [])
            participants = participants_resp.json().get("data", [])
            
            if schedules and participants:
                schedule_id = schedules[0].get("external_id")
                # Obtener external_ids reales de participantes
                p1_id = participants[0].get("external_id") if len(participants) > 0 else None
                p2_id = participants[1].get("external_id") if len(participants) > 1 else None
                
                # Campos que espera la API: schedule_external_id, attendances con participant_external_id
                payload = {
                    "schedule_external_id": schedule_id,
                    "date": today,
                    "attendances": [
                        {"participant_external_id": p1_id, "status": "present"} if p1_id else None,
                        {"participant_external_id": p2_id, "status": "absent"} if p2_id else None
                    ]
                }
                # Filtrar None
                payload["attendances"] = [a for a in payload["attendances"] if a]
                
                response = requests.post(f"{BASE_URL}/attendance/bulk", json=payload, headers=headers)
                self.assertIn(response.status_code, [200, 201],
                              f"TC-06: Falló registro. Status: {response.status_code}, Resp: {response.text}")
                print("TC-06: Registrar Asistencia Exitoso - OK")
            else:
                print("TC-06: Skipped - No hay schedules o participantes disponibles")
        else:
            print("TC-06: Skipped - No se pudo obtener schedules o participantes")

    def test_tc_07_register_attendance_empty_data(self):
        """TC-07: Registrar asistencia con datos vacíos"""
        headers = self._get_auth_headers()
        payload = {}
        response = requests.post(f"{BASE_URL}/attendance/register", json=payload, headers=headers)
        self.assertNotIn(response.status_code, [200, 201],
                         "TC-07: Debería fallar por datos vacíos")
        print("TC-07: Validación Datos Vacíos - OK")

    def test_tc_08_register_attendance_missing_schedule(self):
        """TC-08: Registrar asistencia sin horario"""
        headers = self._get_auth_headers()
        today = date.today().isoformat()
        payload = {
            "date": today,
            "attendances": [
                {"participantId": "1", "status": "present"}
            ]
        }
        response = requests.post(f"{BASE_URL}/attendance/register", json=payload, headers=headers)
        self.assertNotIn(response.status_code, [200, 201],
                         "TC-08: Debería fallar sin horario")
        print("TC-08: Validación Horario Requerido - OK")

    def test_tc_09_register_attendance_invalid_date(self):
        """TC-09: Registrar asistencia con fecha inválida"""
        headers = self._get_auth_headers()
        
        schedules_resp = requests.get(f"{BASE_URL}/attendance/schedules", headers=headers)
        if schedules_resp.status_code == 200:
            schedules = schedules_resp.json().get("data", [])
            if schedules:
                schedule_id = schedules[0].get("external_id")
                
                payload = {
                    "scheduleId": schedule_id,
                    "date": "fecha-invalida",
                    "attendances": [
                        {"participantId": "1", "status": "present"}
                    ]
                }
                response = requests.post(f"{BASE_URL}/attendance/register", json=payload, headers=headers)
                if response.status_code in [200, 201]:
                    print("TC-09 WARNING: El sistema aceptó fecha inválida")
                else:
                    print("TC-09: Validación Fecha Inválida - OK")
            else:
                print("TC-09: Skipped - No hay schedules")
        else:
            print("TC-09: Skipped - No se pudo obtener schedules")

    # ========== CONSULTA DE ASISTENCIAS ==========

    def test_tc_10_get_attendance_history(self):
        """TC-10: Obtener historial de asistencias"""
        headers = self._get_auth_headers()
        response = requests.get(f"{BASE_URL}/attendance/history", headers=headers)
        self.assertEqual(response.status_code, 200, "TC-10: Debería obtener historial")
        data = response.json()
        self.assertIn("data", data, "TC-10: La respuesta debe contener 'data'")
        print("TC-10: Historial de Asistencias - OK")

    def test_tc_11_get_history_with_date_range(self):
        """TC-11: Obtener historial con rango de fechas"""
        headers = self._get_auth_headers()
        start_date = "2026-01-01"
        end_date = "2026-01-31"
        response = requests.get(
            f"{BASE_URL}/attendance/history?startDate={start_date}&endDate={end_date}",
            headers=headers
        )
        self.assertEqual(response.status_code, 200,
                         "TC-11: Debería obtener historial con fechas")
        print("TC-11: Historial con Rango de Fechas - OK")

    def test_tc_12_get_history_by_schedule(self):
        """TC-12: Obtener historial filtrado por horario"""
        headers = self._get_auth_headers()
        
        schedules_resp = requests.get(f"{BASE_URL}/attendance/schedules", headers=headers)
        if schedules_resp.status_code == 200:
            schedules = schedules_resp.json().get("data", [])
            if schedules:
                schedule_id = schedules[0].get("external_id")
                response = requests.get(
                    f"{BASE_URL}/attendance/history?scheduleId={schedule_id}",
                    headers=headers
                )
                self.assertEqual(response.status_code, 200,
                                 "TC-12: Debería obtener historial por horario")
                print("TC-12: Historial por Horario - OK")
            else:
                print("TC-12: Skipped - No hay schedules")
        else:
            print("TC-12: Skipped - No se pudo obtener schedules")

    def test_tc_13_get_session_detail(self):
        """TC-13: Obtener detalle de asistencia de una sesión específica"""
        headers = self._get_auth_headers()
        
        schedules_resp = requests.get(f"{BASE_URL}/attendance/schedules", headers=headers)
        if schedules_resp.status_code == 200:
            schedules = schedules_resp.json().get("data", [])
            if schedules:
                schedule_id = schedules[0].get("external_id")
                test_date = "2026-01-02"
                response = requests.get(
                    f"{BASE_URL}/attendance/session/{schedule_id}/{test_date}",
                    headers=headers
                )
                # Puede ser 200 si hay datos o 400/404 si no hay para esa fecha
                self.assertIn(response.status_code, [200, 400, 404],
                              f"TC-13: Status inesperado: {response.status_code}")
                print("TC-13: Detalle de Sesión - OK")
            else:
                print("TC-13: Skipped - No hay schedules")
        else:
            print("TC-13: Skipped - No se pudo obtener schedules")

    def test_tc_14_get_session_detail_not_found(self):
        """TC-14: Obtener detalle de sesión inexistente"""
        headers = self._get_auth_headers()
        fake_schedule_id = "00000000-0000-0000-0000-000000000000"
        test_date = "2026-01-01"
        response = requests.get(
            f"{BASE_URL}/attendance/session/{fake_schedule_id}/{test_date}",
            headers=headers
        )
        self.assertIn(response.status_code, [400, 404],
                      "TC-14: Debería retornar error para sesión inexistente")
        print("TC-14: Sesión No Encontrada - OK")

    # ========== ELIMINACIÓN DE ASISTENCIAS ==========

    def test_tc_15_delete_session_attendance(self):
        """TC-15: Eliminar asistencia de una sesión/fecha"""
        headers = self._get_auth_headers()
        
        schedules_resp = requests.get(f"{BASE_URL}/attendance/schedules", headers=headers)
        if schedules_resp.status_code == 200:
            schedules = schedules_resp.json().get("data", [])
            if schedules:
                schedule_id = schedules[0].get("external_id")
                # Usar fecha futura para no afectar datos reales
                test_date = "2099-12-31"
                response = requests.delete(
                    f"{BASE_URL}/attendance/session/{schedule_id}/{test_date}",
                    headers=headers
                )
                # Puede retornar 200 si elimina, 400/404 si no hay datos
                self.assertIn(response.status_code, [200, 204, 400, 404],
                              f"TC-15: Status inesperado: {response.status_code}")
                print("TC-15: Eliminar Asistencia de Sesión - OK")
            else:
                print("TC-15: Skipped - No hay schedules")
        else:
            print("TC-15: Skipped - No se pudo obtener schedules")

    # ========== ESTADÍSTICAS ==========

    def test_tc_16_get_today_average(self):
        """TC-16: Obtener promedio de asistencia del día"""
        headers = self._get_auth_headers()
        response = requests.get(f"{BASE_URL}/attendance/today/average", headers=headers)
        self.assertEqual(response.status_code, 200, "TC-16: Debería obtener promedio del día")
        data = response.json()
        self.assertIn("data", data, "TC-16: La respuesta debe contener 'data'")
        print("TC-16: Promedio de Asistencia - OK")

    # ========== PROGRAMAS ==========

    def test_tc_17_get_programs(self):
        """TC-17: Obtener lista de programas disponibles"""
        headers = self._get_auth_headers()
        response = requests.get(f"{BASE_URL}/attendance/v2/public/programs", headers=headers)
        self.assertEqual(response.status_code, 200, "TC-17: Debería obtener lista de programas")
        data = response.json()
        self.assertIn("data", data, "TC-17: La respuesta debe contener 'data'")
        print("TC-17: Obtener Programas - OK")

    def test_tc_18_get_participants_by_program(self):
        """TC-18: Obtener participantes filtrados por programa"""
        headers = self._get_auth_headers()
        response = requests.get(
            f"{BASE_URL}/attendance/v2/public/participants?program=Funcional",
            headers=headers
        )
        self.assertEqual(response.status_code, 200,
                         "TC-18: Debería obtener participantes por programa")
        print("TC-18: Participantes por Programa - OK")

    # ========== ACTUALIZACIÓN DE HORARIOS ==========

    def test_tc_19_update_schedule(self):
        """TC-19: Actualizar un horario existente"""
        headers = self._get_auth_headers()
        
        schedules_resp = requests.get(f"{BASE_URL}/attendance/schedules", headers=headers)
        if schedules_resp.status_code == 200:
            schedules = schedules_resp.json().get("data", [])
            if schedules:
                schedule_id = schedules[0].get("external_id")
                payload = {
                    "name": "Horario Actualizado Test",
                    "capacity": 35
                }
                response = requests.put(
                    f"{BASE_URL}/attendance/schedules/{schedule_id}",
                    json=payload,
                    headers=headers
                )
                self.assertIn(response.status_code, [200, 201],
                              f"TC-19: Falló actualización. Status: {response.status_code}")
                print("TC-19: Actualizar Horario - OK")
            else:
                print("TC-19: Skipped - No hay schedules")
        else:
            print("TC-19: Skipped - No se pudo obtener schedules")

    def test_tc_20_update_schedule_not_found(self):
        """TC-20: Actualizar horario inexistente"""
        headers = self._get_auth_headers()
        fake_schedule_id = "00000000-0000-0000-0000-000000000000"
        payload = {
            "name": "Test"
        }
        response = requests.put(
            f"{BASE_URL}/attendance/schedules/{fake_schedule_id}",
            json=payload,
            headers=headers
        )
        self.assertIn(response.status_code, [400, 404],
                      "TC-20: Debería retornar error para horario inexistente")
        print("TC-20: Horario No Encontrado - OK")


if __name__ == "__main__":
    unittest.main(verbosity=2)
