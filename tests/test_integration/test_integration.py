import uuid
from tests.test_integration.base_test import BaseTestCase


class TestDBHealth(BaseTestCase):

    def test_db_connection_ok(self):
        response = self.client.get("/api/health/db")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["db"], "ok")

    def _login_and_get_token(self):
        payload = {"email": "dev@kallpa.com", "password": "xxxxx"}

        response = self.client.post("/api/auth/login", json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        return data["token"]

    def test_list_users_ok(self):
        token = self._login_and_get_token()

        response = self.client.get(
            "/api/users", headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "ok")
        self.assertIn("data", data)

    def test_save_assessment_ok(self):
        token = self._login_and_get_token()

        # Primero crear un participante para usar su external_id
        participant_payload = {
            "firstName": "Juan",
            "lastName": "Pérez",
            "dni": "1150000001",
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0991234567",
            "email": "juan.test@test.com",
            "address": "Calle Test 123"
        }
        
        participant_resp = self.client.post(
            "/api/save-participants",
            json=participant_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        participant_external_id = participant_resp.get_json()["data"]["participant_external_id"]

        payload = {
            "participant_external_id": participant_external_id,
            "weight": 70,
            "height": 1.70,
            "date": "2026-01-31",
            "waistPerimeter": 80,
            "armPerimeter": 30,
            "legPerimeter": 50,
            "calfPerimeter": 35
        }

        response = self.client.post(
            "/api/save-assessment",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "ok")
        self.assertIn("data", data)
        self.assertIn("external_id", data["data"])
        self.assertIn("bmi", data["data"])
        self.assertIn("status", data["data"])

    # TEST EVALUATION

    def test_list_tests_ok(self):
        token = self._login_and_get_token()

        response = self.client.get(
            "/api/list-test",
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIsInstance(data["data"], list)

    def test_save_test_ok(self):
        token = self._login_and_get_token()

        payload = {
            "name": f"Test RESISTENCIA {uuid.uuid4().hex[:6]}",
            "frequency_months": 3,
            "description": "Evaluación de fuerza",
            "exercises": [
                {"name": "Sentadillas", "unit": "repeticiones"},
                {"name": "Flexiones", "unit": "repetiones"}
            ]
        }

        response = self.client.post(
            "/api/save-test",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        print(response.get_json()) 
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("test_external_id", data["data"])
    
    def test_update_test_ok(self):
        token = self._login_and_get_token()

        # Primero crear un test para usar su external_id
        create_payload = {
            "name": "Test para actualizar",
            "frequency_months": 3,
            "description": "Descripción inicial",
            "exercises": [
                {"name": "Flexiones", "unit": "repeticiones"}
            ]
        }
        
        create_resp = self.client.post(
            "/api/save-test",
            json=create_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        test_external_id = create_resp.get_json()["data"]["test_external_id"]

        payload = {
            "external_id": test_external_id,
            "name": "test fuerza actualizado",
            "frequency_months": 4,
            "description": "Actualizado",
            "exercises": [
                {"name": "Plancha", "unit": "segundos"}
            ]
        }

        response = self.client.put(
            "/api/update-test",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["status"], "ok")

    def test_delete_test_ok(self):
        token = self._login_and_get_token()

        # Primero crear un test para eliminar
        create_payload = {
            "name": "Test para eliminar",
            "frequency_months": 3,
            "description": "Descripción test",
            "exercises": [
                {"name": "Ejercicio test", "unit": "repeticiones"}
            ]
        }
        
        create_resp = self.client.post(
            "/api/save-test",
            json=create_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        test_external_id = create_resp.get_json()["data"]["test_external_id"]

        response = self.client.delete(
            f"/api/delete-test/{test_external_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["status"], "ok")

    # def test_apply_test_ok(self):
    #     token = self._login_and_get_token()

    #     payload = {
    #         "participant_external_id": "d37dfbf2-702b-4c8b-8a0b-45ee1174b57c",
    #         "test_external_id": "2131bd20-abc0-4aa8-8881-14c325bd3959",
    #         "date": "2026-01-31",
    #         "general_observations": "Buen desempeño",
    #         "results": [
    #             {"exercise_external_id": "f622e13b-cd9c-4f11-9dd8-690c7d324e3e", "value": 20},
    #             {"exercise_external_id": "48993c8f-1184-4c6f-a5a4-15fbc300b60d", "value": 15}
    #         ]
    #     }

    #     response = self.client.post(
    #         "/api/apply_test",
    #         json=payload,
    #         headers={"Authorization": f"Bearer {token}"}
    #     )

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.get_json()["status"], "ok")


