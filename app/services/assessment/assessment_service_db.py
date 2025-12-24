from app.models.participant import Participant
from app.models.assessment import Assessment
from app.utils.responses import success_response, error_response
from app import db


class AssessmentServiceDB:
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
        if height and height > 0:
            return round(weight / (height**2), 2)
        return 0

    def get_all_assessments(self):
        try:
            assessments = Assessment.query.all()

            data = [
                {
                    "external_id": a.external_id,
                    "participant_external_id": a.participant.external_id,
                    "participant_name": f"{a.participant.firstName} {a.participant.lastName}",
                    "age": a.participant.age,
                    "date": a.date,
                    "weight": a.weight,
                    "height": a.height,
                    "waistPerimeter": a.waistPerimeter,
                    "wingspan": a.wingspan,
                    "bmi": a.bmi,
                    "status": a.status
                }
                for a in assessments
            ]

            return success_response(
                msg="Evaluaciones listadas correctamente",
                data=data,
            )

        except Exception as e:
            return error_response(msg=f"Error interno del servidor: {str(e)}", code=500)

    def register_evaluation(self, data):
        try:
            errors = {}
            participant_external_id = data.get("participant_external_id")
            if not participant_external_id:
                errors["participant_external_id"] = "Seleccionar un participante"
            else:
                participant = Participant.query.filter_by(
                    external_id=participant_external_id
                ).first()
                if not participant:
                    errors["participant_external_id"] = "Participante no encontrado"
            weight = data.get("weight")
            if weight is None or weight <= 0:
                errors["weight"] = "El peso debe ser un número mayor que 0"

            height = data.get("height")
            if height is None or height <= 0:
                errors["height"] = "La altura debe ser un número mayor que 0"

            date = data.get("date")
            if not date:
                errors["date"] = "Seleccionar una fecha válida"

            if errors:
                return {
                    "code": 400,
                    "status": "error",
                    "msg": "Error de validación",
                    "errors": errors,
                    "data": None,
                }

            waistPerimeter = data.get("waistPerimeter")
            wingspan = data.get("wingspan")

            bmi = self.calculateBMI(weight, height)

            if participant.age >= 18:
                status = self.classify_bmi_adult(bmi)
            else:
                status = "Pendiente (menor de edad)"

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

    def update_assessment(self, external_id, data):
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
