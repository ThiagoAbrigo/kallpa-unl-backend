from datetime import datetime, timedelta
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

    def register_evaluation(self, data):
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
            participant = Participant.query.filter_by(external_id=participant_external_id).first()
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

    def get_assessments_by_participant_external_id(self, participant_external_id):
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

    def get_average_bmi(self):
        try:
            # Obtener todos los IMC registrados
            all_bmis = db.session.query(Assessment.bmi).all()

            if not all_bmis:
                return {
                    "code": 200,
                    "status": "ok",
                    "msg": "No hay evaluaciones registradas",
                    "data": {"average_bmi": None},
                }

            # Calcular promedio
            total_bmi = sum(bmi for (bmi,) in all_bmis)
            count = len(all_bmis)
            average_bmi = total_bmi / count

            return {
                "code": 200,
                "status": "ok",
                "msg": "Promedio de IMC calculado correctamente",
                "data": {"average_bmi": round(average_bmi, 2)},
            }
        except Exception as e:
            return {
                "code": 500,
                "status": "error",
                "msg": f"Error interno: {str(e)}",
                "data": None,
            }

    def get_anthropometric_history(self, months: int = 3):
        today = datetime.now()
        start_date = today - timedelta(days=30 * months)

        # Convertimos start_date a string para comparar con Assessment.date
        start_date_str = start_date.strftime("%Y-%m-%d")

        # Traer todas las evaluaciones desde start_date_str
        assessments = (
            Assessment.query
            .filter(Assessment.date >= start_date_str)
            .order_by(Assessment.date.asc())
            .all()
        )

        if not assessments:
            return success_response(msg="No hay evaluaciones en este período", data=[])

        # Lista de valores de IMC para cada evaluación
        bmi_values = [a.bmi for a in assessments]

        # Promedios generales
        avg_weight = round(sum(a.weight for a in assessments) / len(assessments), 2)
        avg_height = round(sum(a.height for a in assessments) / len(assessments), 2)
        avg_bmi = round(sum(bmi_values) / len(bmi_values), 2)

        # Preparar datos individuales por fecha
        data = [
            {
                "date": a.date,  # ya es string
                "weight": a.weight,
                "height": a.height,
                "bmi": a.bmi,
            }
            for a in assessments
        ]

        response_data = {
            "period_months": months,
            "average": {
                "weight": avg_weight,
                "height": avg_height,
                "bmi": avg_bmi,
            },
            "assessments": data,
        }

        return success_response(
            msg=f"Historial antropométrico últimos {months} meses",
            data=response_data
        )