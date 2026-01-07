import unittest
import requests
import json
import uuid
import random
import string

BASE_URL = "http://127.0.0.1:5000/api"

class TestFinales(unittest.TestCase):
    def _generate_numeric_string(self, length):
        return ''.join(random.choices(string.digits, k=length))
    
    def setUp(self):
        self.headers = {"Content-Type": "application/json"}
        # Precondición: Usuario administrador debe existir
        self.admin_email = "admin@kallpa.com"
        self.admin_password = "123456" 
        self.token = None

    def _get_auth_headers(self):
        if not self.token:
             payload = {"email": self.admin_email, "password": self.admin_password}
             resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
             if resp.status_code == 200:
                 self.token = resp.json()["token"]
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def test_tc_01_register_participant(self):
        """TC-01: Registrar Participante - Adulto Funcional Exitoso (Antes TC-05)"""
        # Precondiciones: Token válido, datos únicos
        
        # Generar DNI válido que inicie con 0 (no secuencial)
        unique_suffix = str(uuid.uuid4().int)[:9]
        unique_dni = f"0{unique_suffix}"
        
        payload = {
            "firstName": "Juan",
            "lastName": "Pérez",
            "dni": unique_dni,
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0991234567",
            "email": f"juan.{unique_dni}@test.com",
            "address": "Calle Falsa 123"
        }
        
        headers = self._get_auth_headers()
        # Verificar que se obtuvo el token (Autenticación exitosa)
        self.assertTrue(headers.get("Authorization"), "No se pudo obtener el token de autorización")

        response = requests.post(f"{BASE_URL}/save-participants", json=payload, headers=headers)
        
        # Postcondición: Registro exitoso (200 o 201)
        self.assertIn(response.status_code, [200, 201], f"TC-01: Falló registro. Status: {response.status_code}, Resp: {response.text}")
        
        # Validar estructura de respuesta
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("participant_external_id", data["data"])
        
        print("TC-01: Registro Participante Exitoso - Correcto")

    def test_tc_02_register_duplicate(self):
        """TC-02: Registrar Participante - Validación Duplicado (Antes TC-06)"""
        headers = self._get_auth_headers()
        self.assertTrue(headers.get("Authorization"), "No se pudo obtener el token de autorización")
        
        # DNI válido con todos los campos requeridos
        unique_suffix = str(uuid.uuid4().int)[:9]
        dni = f"0{unique_suffix}"
        
        payload_1 = {
            "firstName": "Ana",
            "lastName": "Loja",
            "dni": dni,
            "age": 22,
            "address": "Calle Test",
            "phone": "0998877665",
            "email": f"ana{dni}@test.com",
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE"
        }
        
        # Paso 1: Primer registro (Precondición para el test de duplicado)
        resp1 = requests.post(f"{BASE_URL}/save-participants", json=payload_1, headers=headers)
        self.assertIn(resp1.status_code, [200, 201], "Fallo en la precondición: No se pudo crear el primer registro")

        # Paso 2: Intento de registro duplicado
        response = requests.post(f"{BASE_URL}/save-participants", json=payload_1, headers=headers)
        
        # Validar que rechace el duplicado
        if response.status_code == 200 or response.status_code == 201:
             print("TC-02 WARNING: El sistema permitió duplicado (puede ser actualización).")
             # Dependiendo de la lógica de negocio, esto podría ser un fallo
             self.fail("TC-02: El sistema permitió registrar un duplicado")
        else:
             self.assertEqual(response.status_code, 400, "TC-02: Debería reportar error de duplicado")
             resp_json = response.json()
             self.assertIn("data", resp_json)
             # Verificar que los errores sean específicos de duplicidad
             logging_err = resp_json.get("data", {})
             self.assertTrue("dni" in logging_err or "email" in logging_err, "Debe indicar error en DNI o Email")
             print(f"TC-02: Validación Duplicado - Error recibido: {response.text} - Correcto")

    def test_tc_03_registro_exitoso_medidas_antropometricas(self):
        """TC-03: Registro de medidas antropometricas - Registro Exitoso"""
        unique_id = str(uuid.uuid4())[:8]
        participant_payload = {
            "firstName": "Carlos",
            "lastName": "Lopez",
            "dni": f"10{self._generate_numeric_string(8)}",
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0999999999",
            "email": f"carlos{unique_id}@test.com",
            "address": "Av. Siempre Viva"
        }

        response_participant = requests.post(
            f"{BASE_URL}/save-participants",
            json=participant_payload,
            headers=self._get_auth_headers()
        )

        self.assertIn(response_participant.status_code, [200, 201])

        participant_external_id = response_participant.json()["data"]["participant_external_id"]

        assessment_payload = {
            "participant_external_id": participant_external_id,
            "weight": 70,
            "height": 1.75,
            "waistPerimeter": 80,
            "wingspan": 170,
            "date": "2025-01-05"
        }

        response_assessment = requests.post(
            f"{BASE_URL}/save-assessment",
            json=assessment_payload,
            headers=self._get_auth_headers()
        )
        if response_assessment.status_code != 200:
            print("Error al registrar medidas (TC-03):", response_assessment.json())
        else:
            data = response_assessment.json()["data"]
            print("Registro de Medidas Exitoso (TC-03):", data)

    def test_tc_04_registro_medidas_altura_fuera_de_rango(self):
        """TC-04: Registro de medidas antropométricas - Altura fuera de rango"""

        unique_id = str(uuid.uuid4())[:8]
        participant_payload = {
            "firstName": "Luis",
            "lastName": "Gomez",
            "dni": f"12{self._generate_numeric_string(8)}",
            "age": 28,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0997777777",
            "email": f"luis{unique_id}@test.com",
            "address": "Av Central"
        }

        response_participant = requests.post(
            f"{BASE_URL}/save-participants",
            json=participant_payload,
            headers=self._get_auth_headers()
        )

        self.assertIn(response_participant.status_code, [200, 201])

        participant_external_id = response_participant.json()["data"]["participant_external_id"]

        # Altura completamente inválida
        assessment_payload = {
            "participant_external_id": participant_external_id,
            "weight": 70,
            "height": 3000,  #Valor irreal
            "waistPerimeter": 80,
            "wingspan": 170,
            "date": "2025-01-05"
        }

        response_assessment = requests.post(
            f"{BASE_URL}/save-assessment",
            json=assessment_payload,
            headers=self._get_auth_headers()
        )
        if response_assessment.status_code != 200:
            print("Error al registrar medidas (TC-04):", response_assessment.json())
        else:
            data = response_assessment.json()["data"]
            print("Registro de Medidas Exitoso (TC-04):", data)


    def _get_random_time_slot(self):
        """Genera un slot de tiempo aleatorio para evitar solapamientos en tests"""
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        day = random.choice(days)
        # Random start hour and MINUTE to minimize collisions
        start_h = random.randint(7, 21)
        start_m = random.randint(0, 59)
        
        # End time = Start + 1 hour (approx)
        end_h = start_h + 1
        return day, f"{start_h:02d}:{start_m:02d}", f"{end_h:02d}:{start_m:02d}"

    def test_tc_05_create_schedule(self):
        """TC-05: Crear Horario/Sesión - Con reintento por solapamiento (Migrado de TC-01)"""
        max_retries = 10
        for i in range(max_retries):
            day, start, end = self._get_random_time_slot()
            payload = {
                "name": f"Sesión TC-05 {uuid.uuid4().hex[:4]}",
                "startTime": start,
                "endTime": end,
                "program": "FUNCIONAL",
                "maxSlots": 20,
                "dayOfWeek": day
            }
            resp = requests.post(f"{BASE_URL}/attendance/v2/public/schedules", json=payload, headers=self._get_auth_headers())
            if resp.status_code in [200, 201]:
                print(f"TC-05: Horario creado -> {resp.json()}")
                return
            
            # If overlap, retry
            if resp.status_code == 400 and "solapa" in resp.text:
                continue
            
            # If other error, fail
            self.fail(f"TC-05 Fallo: {resp.text}")
        
        self.fail(f"TC-05: No se pudo crear horario tras {max_retries} intentos")

    def test_tc_06_create_schedule_missing_fields(self):
        """TC-06: Crear Horario - Faltan campos (Negativo) (Migrado de TC-04)"""
        # Missing startTime and endTime
        payload = {
            "name": "Sesión Incompleta TC-06",
            "program": "FUNCIONAL",
            "dayOfWeek": "MONDAY"
        }
        resp = requests.post(
            f"{BASE_URL}/attendance/v2/public/schedules", 
            json=payload, 
            headers=self._get_auth_headers()
        )
        self.assertEqual(resp.status_code, 400, f"TC-06: Debería fallar por campos faltantes. Status: {resp.status_code}")
        self.assertIn("Faltan campos requeridos", resp.text)
        print("TC-06: Validación de campos faltantes correcta")

    def test_tc_07_registro_test_exitoso(self):
        """TC-07: Registro de Test - Test creado correctamente"""
        unique_id = str(uuid.uuid4())[:8]
        test_payload = {
            "name": f"Test de hipertrofia {unique_id}",
            "description": "Primer test de hipertrofia, frecuencia 3",
            "frequency_months": 3,
            "observations": "Primer test",
            "exercises": [
                {"name": "Press Banca", "unit": "repeticiones"},
                {"name": "Sentadilla", "unit": "repeticiones"},
                {"name": "Burpees", "unit": "repeticiones"}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/save-test",
            json=test_payload,
            headers=self._get_auth_headers()
        )

        self.assertIn(response.status_code, [200, 201])
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("test_external_id", data["data"])
        self.assertEqual(data.get("msg"), "Test creado correctamente")
        print("Registro de Test Exitoso (TC-02):", data)

    def test_tc_08_registro_test_sin_ejercicios(self):
        """TC-08: Registro de Test - Falla por campos de ejercicios vacíos"""
        unique_id = str(uuid.uuid4())[:8]
        test_payload = {
            "name": f"Test Sin Ejercicios {unique_id}",
            "description": "Test sin ejercicios llenos",
            "frequency_months": 3,
            "observations": "Segundo test",
            "exercises": [  # Aquí siempre hay un objeto, pero vacíos
                {"name": "", "unit": ""}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/save-test",
            json=test_payload,
            headers=self._get_auth_headers()
        )

        data = response.json()
        self.assertIn("exercises", data.get("errors", {}) or data.get("msg", {}))
        exercises_error = data.get("errors", {}).get("exercises") or data.get("msg", {}).get("exercises")
        self.assertEqual(exercises_error, "Complete los campos de los ejercicios")
        print("Error al registrar Test con ejercicios vacíos (TC-03):", data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
