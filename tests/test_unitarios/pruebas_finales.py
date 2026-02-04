import unittest
from unittest.mock import patch, MagicMock
from app.controllers.usercontroller import UserController
from app.controllers.assessment_controller import AssessmentController

class TestFinales(unittest.TestCase):
    """Pruebas Unitarias con Mocks """

    def setUp(self):
        pass

    @patch("app.controllers.usercontroller.UserController._get_token")
    @patch("app.controllers.usercontroller.Participant")
    @patch("app.controllers.usercontroller.db.session")
    @patch("app.controllers.usercontroller.java_sync")
    def test_tc_01_register_participant(self, mock_java_sync, mock_session, mock_participant, mock_get_token):
        """TC-01: Registrar Participante - Adulto Funcional Exitoso"""
        mock_get_token.return_value = "Bearer mock_token"
        mock_participant.query.filter_by.return_value.first.return_value = None
        mock_java_sync.search_by_identification.return_value = {"found": False}
        
        fake_participant = MagicMock()
        fake_participant.external_id = "uuid-ext-id"
        mock_participant.return_value = fake_participant

        data = {
            "firstName": "Juan",
            "lastName": "Pérez",
            "dni": "1100000001",
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0991234567",
            "email": "juan@test.com",
            "address": "Calle Falsa 123"
        }
        
        controller = UserController()
        response = controller.create_participant(data)
        
        self.assertEqual(response["code"], 200)
        self.assertEqual(response["msg"], "Participante registrado correctamente")
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch("app.controllers.usercontroller.UserController._get_token")
    @patch("app.controllers.usercontroller.Participant")
    def test_tc_02_register_duplicate(self, mock_participant, mock_get_token):
        """TC-02: Registrar Participante - Validación Duplicado (DNI local)"""
        mock_get_token.return_value = "Bearer mock_token"
        mock_participant.query.filter_by.return_value.first.return_value = MagicMock()
        
        data = {
            "firstName": "Ana",
            "lastName": "Loja",
            "dni": "1100000001",
            "age": 22,
            "address": "Calle Test",
            "phone": "0987654321",
            "email": "ana@test.com",
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE"
        }
        
        controller = UserController()
        response = controller.create_participant(data)
        
        self.assertEqual(response["code"], 400)
        self.assertIn("dni", response["data"])
        self.assertEqual(response["data"]["dni"], "El DNI ya está registrado")

    @patch("app.controllers.assessment_controller.Participant")
    @patch("app.controllers.assessment_controller.Assessment")
    @patch("app.controllers.assessment_controller.db.session")
    @patch("app.controllers.assessment_controller.log_activity")
    def test_tc_03_registro_exitoso_medidas_antropometricas(self, mock_log, mock_session, mock_assessment, mock_participant):
        """TC-03: Registro de medidas antropometricas - Exitoso"""
        fake_participant = MagicMock()
        fake_participant.id = 1
        fake_participant.external_id = "uuid-ext-id"
        fake_participant.firstName = "Carlos"
        fake_participant.lastName = "Lopez"
        mock_participant.query.filter_by.return_value.first.return_value = fake_participant
        
        fake_assessment_instance = MagicMock()
        fake_assessment_instance.external_id = "assessment-uuid"
        fake_assessment_instance.bmi = 22.86
        fake_assessment_instance.status = "Peso adecuado"
        mock_assessment.return_value = fake_assessment_instance

        assessment_payload = {
            "participant_external_id": "uuid-ext-id",
            "weight": 70,
            "height": 1.75,
            "waistPerimeter": 0.80,
            "wingspan": 1.70,
            "date": "2025-01-05"
        }

        controller = AssessmentController()
        response = controller.register(assessment_payload)
        
        self.assertEqual(response["code"], 200)
        self.assertEqual(response["msg"], "Evaluación registrada exitosamente")
        self.assertEqual(response["data"]["participant_external_id"], "uuid-ext-id")
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

if __name__ == "__main__":
    unittest.main(verbosity=2)
