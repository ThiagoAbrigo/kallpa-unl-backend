import unittest
import requests
import uuid

BASE_URL = "http://127.0.0.1:5000/api"

class TestMockScenarios(unittest.TestCase):
    def setUp(self):
        self.headers = {"Content-Type": "application/json"}
        self.admin_email = "admin@kallpa.com"
        self.admin_password = "123456"
        self.token = None

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

    def test_tc_02_registro_test_exitoso(self):
        """TC-02: Registro de Test - Test creado correctamente"""
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

    def test_tc_03_registro_test_sin_ejercicios(self):
        """TC-03: Registro de Test - Falla por campos de ejercicios vacíos"""
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
