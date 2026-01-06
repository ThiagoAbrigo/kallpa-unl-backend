from app.models.assessment import Assessment
from app.models.participant import Participant
from app.services.activity_service import log_activity
from app.utils.responses import error_response, success_response
from app import db
from sqlalchemy import func

class AssessmentController:
    def classify_bmi_adult(self, bmi):
        if bmi < 18.5:
            return "Bajo peso"
        elif bmi < 25:
            return "Peso adecuado"
        elif bmi < 30:
            return "Sobrepeso"
        else:
            return "Obesidad"
    
    def calculateBMI(self, weight, height):
        if height <= 0 or weight <= 0:
            return None
        return round(weight / (height ** 2), 2)

    def get_assessment(self):
        try:
            assessments = Assessment.query.all()

            data = [
                {
                    "external_id": a.external_id,
                    "participant_external_id": a.participant.external_id,
                    "participant_name": f"{a.participant.firstName} {a.participant.lastName}",
                    "dni": a.participant.dni,
                    "age": a.participant.age,
                    "date": a.date,
                    "weight": a.weight,
                    "height": a.height,
                    "waistPerimeter": a.waistPerimeter,
                    "wingspan": a.wingspan,
                    "bmi": a.bmi,
                    "status": a.status,
                }
                for a in assessments
            ]

            return success_response(
                msg="Evaluaciones listadas correctamente",
                data=data,
            )

        except Exception as e:
            return error_response(msg=f"Error interno del servidor: {str(e)}", code=500)

    def register(self, data):
        try:
            errors = {}

            # Campos principales
            participant_external_id = data.get("participant_external_id")
            weight = data.get("weight")
            height = data.get("height")
            date = data.get("date")

            # Si los tres campos principales están vacíos, error general
            if not participant_external_id and not weight and not height:
                errors["general"] = "Campos requeridos: participante, peso y altura"

            # Validación individual (opcional)
            if not participant_external_id:
                errors["participant_external_id"] = "Campo requerido"
            if not weight:
                errors["weight"] = "Campo requerido"
            if not height:
                errors["height"] = "Campo requerido"
            if not date:
                errors["date"] = "Campo requerido"

            # Retornar errores si existen
            if errors:
                return {
                    "code": 400,
                    "status": "error",
                    "msg": "Error de validación",
                    "errors": errors,
                    "data": None,
                }

            # Buscar participante
            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()
            if not participant:
                return {
                    "code": 400,
                    "status": "error",
                    "msg": "Error de validación",
                    "errors": {"participant_external_id": "Participante no encontrado"},
                    "data": None,
                }

            waistPerimeter = data.get("waistPerimeter")
            wingspan = data.get("wingspan")

            # Validación de altura
            if height <= 0 or height < 0.8 or height > 2.5:
                errors["height"] = "La altura debe estar entre 0.8 y 2.5 metros"
            
            if errors:
                return {
                    "code": 400,
                    "status": "error",
                    "msg": "Error de validación",
                    "errors": errors,
                    "data": None,
                }
            # Calcular IMC para todos
            bmi = self.calculateBMI(weight, height)
            
            # Asignar status según IMC (sin considerar edad)
            status = self.classify_bmi_adult(bmi)

            # Crear evaluación
            assessment = Assessment(
                participant_id=participant.id,
                date=date,
                weight=weight,
                height=height,
                waistPerimeter=waistPerimeter,
                wingspan=wingspan,
                bmi=bmi,
                status=status,
            )

            db.session.add(assessment)

            log_activity(
                type="MEDICIOOON",
                title="Medición registrada",
                description=f"Se registró una evaluación para {participant.firstName} {participant.lastName}",
            )
            db.session.commit()
            return {
                "code": 200,
                "status": "ok",
                "msg": "Evaluación registrada exitosamente",
                "data": {
                    "external_id": assessment.external_id,
                    "participant_external_id": participant.external_id,
                    "bmi": assessment.bmi,
                    "status": assessment.status,
                },
            }

        except Exception as e:
            db.session.rollback()
            return {
                "code": 500,
                "status": "error",
                "msg": f"Internal error: {str(e)}",
                "data": None,
            }

    def update(self, external_id, data):
        try:
            assessment = Assessment.query.filter_by(external_id=external_id).first()

            if not assessment:
                return error_response("Evaluación no encontrada")

            assessment.date = data.get("date", assessment.date)
            assessment.weight = data.get("weight", assessment.weight)
            assessment.height = data.get("height", assessment.height)
            assessment.waistPerimeter = data.get(
                "waistPerimeter", assessment.waistPerimeter
            )
            assessment.wingspan = data.get("wingspan", assessment.wingspan)

            # Recalcular IMC
            assessment.bmi = self.calculateBMI(assessment.weight, assessment.height)

            db.session.commit()

            return success_response(
                msg="Evaluación actualizada correctamente",
                data={
                    "external_id": assessment.external_id,
                    "participant_external_id": assessment.participant.external_id,
                    "bmi": assessment.bmi,
                },
            )

        except Exception as e:
            db.session.rollback()
            return error_response(msg=f"Error interno del servidor: {str(e)}", code=500)

    def get_participants_external_id(self, participant_external_id):
        try:
            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()

            if not participant:
                return error_response(msg="Participante no encontrado", code=404)

            assessments = (
                Assessment.query.filter_by(participant_id=participant.id)
                .order_by(Assessment.date.desc())
                .all()
            )

            data = [
                {
                    "external_id": a.external_id,
                    "date": a.date,
                    "weight": a.weight,
                    "height": a.height,
                    "waistPerimeter": a.waistPerimeter,
                    "wingspan": a.wingspan,
                    "bmi": a.bmi,
                    "status": a.status,
                }
                for a in assessments
            ]

            return success_response(
                msg="Evaluaciones del participante listadas correctamente",
                data={
                    "participant": {
                        "external_id": participant.external_id,
                        "firstName": f"{participant.firstName} {participant.lastName}",
                        "dni": participant.dni,
                        "age": participant.age,
                    },
                    "assessments": data,
                },
            )

        except Exception as e:
            return error_response(msg=str(e), code=500)
    
    def get_bmi_distribution(self):
        try:
            results = (
                db.session.query(Assessment.status, func.count(Assessment.id))
                .group_by(Assessment.status)
                .all()
            )

            labels = ["Bajo peso", "Peso adecuado", "Sobrepeso", "Obesidad"]

            data_map = {label: 0 for label in labels}

            for status, count in results:
                if status in data_map:
                    data_map[status] = count

            chart_data = [
                {"label": label, "value": data_map[label]} for label in labels
            ]

            return {
                "code": 200,
                "status": "ok",
                "msg": "Distribución por estado nutricional",
                "data": chart_data,
            }

        except Exception as e:
            return {"code": 500, "status": "error", "msg": str(e), "data": None}

        
