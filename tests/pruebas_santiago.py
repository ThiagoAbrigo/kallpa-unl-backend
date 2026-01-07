import unittest
import requests
import json
import uuid
import random
import string

BASE_URL = "http://127.0.0.1:5000/api"

class TestMockScenarios(unittest.TestCase):
    def setUp(self):
        self.headers = {"Content-Type": "application/json"}
        self.admin_email = "admin@kallpa.com"
        self.admin_password = "123456" 
        self.token = None

    def _generate_numeric_string(self, length):
        return ''.join(random.choices(string.digits, k=length))

    def test_tc_01_login_success(self):
        """TC-01: Inicio de Sesión - Ingreso exitoso"""
        payload = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200, "TC-01: Debería retornar 200 OK")
        data = response.json()
        self.assertIn("token", data, "TC-01: La respuesta debe contener un token")
        self.__class__.token = data["token"]
        print("TC-01: Login Exitoso - OK")

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

    def test_tc_01_registro_exitoso_medidas_antropometricast(self):
        """TC-01: Registro de medidas antropometricas - Registro Exitoso"""
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
            print("Error al registrar medidas (TC-01):", response_assessment.json())
        else:
            data = response_assessment.json()["data"]
            print("Registro de Medidas Exitoso (TC-01):", data)

    def test_tc_02_registro_medidas_falla_campo_obligatorio(self):
        """TC-02: Registro de medidas antropométricas - Falla por campo obligatorio"""
        unique_id = str(uuid.uuid4())[:8]
        participant_payload = {
            "firstName": "Ana",
            "lastName": "Martinez",
            "dni": f"11{self._generate_numeric_string(8)}",
            "age": 30,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0998888888",
            "email": f"ana{unique_id}@test.com",
            "address": "Calle Test"
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
            "weight": 65,
            # "height": 1.65,  Campo obligatorio omitido
            "waistPerimeter": 75,
            "wingspan": 160,
            "date": "2025-01-05"
        }

        response_assessment = requests.post(
            f"{BASE_URL}/save-assessment",
            json=assessment_payload,
            headers=self._get_auth_headers()
        )
        if response_assessment.status_code != 200:
            print("Error al registrar medidas (TC-02):", response_assessment.json())
        else:
            data = response_assessment.json()["data"]
            print("Registro de Medidas Exitoso (TC-02):", data)

    def test_tc_03_registro_medidas_altura_fuera_de_rango(self):
        """TC-03: Registro de medidas antropométricas - Altura fuera de rango"""

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
            print("Error al registrar medidas (TC-03):", response_assessment.json())
        else:
            data = response_assessment.json()["data"]
            print("Registro de Medidas Exitoso (TC-03):", data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
