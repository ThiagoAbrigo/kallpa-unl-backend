"""Assessment Service DB - Business logic for assessments using DAO pattern"""
from app.dao.assessment_dao import AssessmentDAO
from app.schemas.assessment_schema import assessment_schema, assessments_schema


class AssessmentServiceDB:
    """Service for assessment operations using database"""
    
    def __init__(self):
        self.assessment_dao = AssessmentDAO()
    
    def registrar_evaluacion(self, data):
        """Register a new assessment"""
        try:
            # Validate required fields
            required_fields = ["participant_id", "fecha", "peso", "talla", "perimetroCintura", "envergadura"]
            if not all(k in data for k in required_fields):
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": f"Campos requeridos: {', '.join(required_fields)}"
                }
            
            # Create assessment using DAO
            assessment = self.assessment_dao.create(
                participant_id=data["participant_id"],
                fecha=data["fecha"],
                peso=data["peso"],
                talla=data["talla"],
                perimetroCintura=data["perimetroCintura"],
                envergadura=data["envergadura"]
            )
            
            # Calculate IMC
            assessment.calcularIMC()
            
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Evaluación registrada en BD",
                "data": assessment_schema.dump(assessment)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error al registrar evaluación: {str(e)}"
            }
    
    def obtener_evaluaciones_participante(self, participant_id):
        """Get all assessments for a participant"""
        try:
            assessments = self.assessment_dao.get_by_participant_id(participant_id)
            return {
                "status": "ok",
                "origen": "db",
                "msg": f"Se encontraron {len(assessments)} evaluaciones",
                "data": assessments_schema.dump(assessments)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error: {str(e)}"
            }
    
    def obtener_ultima_evaluacion(self, participant_id):
        """Get the latest assessment for a participant"""
        try:
            assessment = self.assessment_dao.get_latest_by_participant(participant_id)
            if not assessment:
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": "No se encontró evaluación"
                }
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Evaluación encontrada",
                "data": assessment_schema.dump(assessment)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error: {str(e)}"
            }
    
    def editar_evaluacion(self, assessment_id, data):
        """Edit an assessment"""
        try:
            assessment = self.assessment_dao.update(assessment_id, **data)
            if not assessment:
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": "Evaluación no encontrada"
                }
            
            # Recalculate IMC if peso or talla changed
            if "peso" in data or "talla" in data:
                assessment.calcularIMC()
            
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Evaluación actualizada",
                "data": assessment_schema.dump(assessment)
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error: {str(e)}"
            }
    
    def eliminar_evaluacion(self, assessment_id):
        """Delete an assessment"""
        try:
            deleted = self.assessment_dao.delete(assessment_id)
            if not deleted:
                return {
                    "status": "error",
                    "origen": "db",
                    "msg": "Evaluación no encontrada"
                }
            return {
                "status": "ok",
                "origen": "db",
                "msg": "Evaluación eliminada"
            }
        except Exception as e:
            return {
                "status": "error",
                "origen": "db",
                "msg": f"Error: {str(e)}"
            }
