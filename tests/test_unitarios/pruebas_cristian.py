import unittest
from unittest.mock import patch, MagicMock
from app.controllers.evaluation_controller import EvaluationController
from app import create_app


class TestEvaluationController(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.controller = EvaluationController()

    # TC-02: Registro de Test - Test creado correctamente
    @patch("app.utils.validations.evaluation_validation.Test")  # Mock del Test en la validación
    @patch("app.utils.validations.evaluation_validation.db.func") # Mock del db.func en la validación
    @patch("app.controllers.evaluation_controller.db.session")
    @patch("app.controllers.evaluation_controller.TestExercise")
    @patch("app.controllers.evaluation_controller.Test")
    def test_tc_02_registro_test_exitoso(
        self, mock_test_controller, mock_test_exercise, mock_session, mock_func_validation, mock_test_validation
    ):
        with self.app.app_context():
            fake_test = MagicMock()
            fake_test.id = 1
            fake_test.external_id = "test-123"

            # Mock en la validación (donde falla)
            mock_test_validation.query.filter.return_value.first.return_value = None  # No existe duplicado
            
            # Mock en el controlador
            mock_test_controller.return_value = fake_test

            data = {
                "name": "Test de hipertrofia",
                "description": "Primer test de hipertrofia",
                "frequency_months": 3,
                "exercises": [
                    {"name": "Press Banca", "unit": "repeticiones"},
                ],
            }

            result = self.controller.register(data)

            self.assertEqual(result["code"], 200)
            self.assertEqual(result["status"], "ok")
            self.assertIn("test_external_id", result["data"])

            mock_session.add.assert_called()
            mock_session.commit.assert_called_once()

    # TC-03: Registro de Test - Falla por ejercicios vacíos
    @patch("app.utils.validations.evaluation_validation.Test")
    @patch("app.utils.validations.evaluation_validation.db.func")
    @patch("app.controllers.evaluation_controller.db.session")
    @patch("app.controllers.evaluation_controller.Test")
    def test_tc_03_registro_test_sin_ejercicios(
        self, mock_test_controller, mock_session, mock_func_validation, mock_test_validation
    ):
        with self.app.app_context():
            # Mock en la validación para que no falle por nombre duplicado
            mock_test_validation.query.filter.return_value.first.return_value = None

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
            # El mensaje podría incluir información sobre errores en exercises
            # pero verificar que hay errores de validación relacionados con ejercicios
            self.assertIn("validación", result["msg"].lower())

            mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
