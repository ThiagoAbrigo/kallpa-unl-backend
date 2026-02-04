import unittest
from unittest.mock import patch, MagicMock
from app.controllers.evaluation_controller import EvaluationController


class TestEvaluationController(unittest.TestCase):

    def setUp(self):
        self.controller = EvaluationController()

    # TC-02: Registro de Test - Test creado correctamente
    @patch("app.controllers.evaluation_controller.db.session")
    @patch("app.controllers.evaluation_controller.TestExercise")
    @patch("app.controllers.evaluation_controller.Test")
    def test_tc_02_registro_test_exitoso(
        self, mock_test, mock_test_exercise, mock_session
    ):
        fake_test = MagicMock()
        fake_test.id = 1
        fake_test.external_id = "test-123"

        mock_test.query.filter_by.return_value.first.return_value = None
        mock_test.return_value = fake_test

        data = {
            "name": "Test de hipertrofia",
            "description": "Primer test de hipertrofia",
            "frequency_months": 3,
            "exercises": [
                {"name": "Press Banca", "unit": "repeticiones"},
            ],
        }

        result = self.controller.register(data)

        print(result["msg"])

        self.assertEqual(result["code"], 200)
        self.assertEqual(result["status"], "ok")
        self.assertIn("test_external_id", result["data"])

        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()

    # TC-03: Registro de Test - Falla por ejercicios vacíos
    @patch("app.controllers.evaluation_controller.db.session")
    @patch("app.controllers.evaluation_controller.Test")
    def test_tc_03_registro_test_sin_ejercicios(
        self, mock_test, mock_session
    ):
        mock_test.query.filter_by.return_value.first.return_value = None

        data = {
            "name": "Test sin ejercicios",
            "description": "Test inválido",
            "frequency_months": 3,
            "exercises": [
                {"name": "", "unit": ""}
            ],
        }

        result = self.controller.register(data)

        print(result["msg"])

        self.assertEqual(result["code"], 400)
        self.assertEqual(result["status"], "error")
        self.assertIn("exercises", result["msg"])

        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
