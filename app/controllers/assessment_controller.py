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
        return round(weight / (height**2), 2)

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
                    "bmi": a.bmi,
                    "status": a.status,
                }
                for a in assessments
            ]

            return success_response(
                msg="Evaluaciones listadas correctamente", data=data, code=200
            )

        except Exception as e:
            return error_response(msg=f"Error interno del servidor: {str(e)}", code=500)

    def register(self, data):
        try:
            errors = {}
            # 1. Obtener campos
            participant_external_id = data.get("participant_external_id")
            weight = data.get("weight")
            height = data.get("height")
            date = data.get("date")
            waistPerimeter = data.get("waistPerimeter")
            armPerimeter = data.get("armPerimeter")
            legPerimeter = data.get("legPerimeter")
            calfPerimeter = data.get("calfPerimeter")

            # 2. Validar existencia (obligatorios)
            if not participant_external_id or not str(participant_external_id).strip():
                errors["participant_external_id"] = "Selecciona un participante"

            if weight is None:
                errors["weight"] = "Campo requerido"

            if height is None:
                errors["height"] = "Campo requerido"

            if date is None:
                errors["date"] = "Campo requerido"

            if waistPerimeter is None:
                waistPerimeter = 0

            if armPerimeter is None:
                armPerimeter = 0

            if legPerimeter is None:
                legPerimeter = 0

            if calfPerimeter is None:
                calfPerimeter = 0

            # 3. Validar tipos (letras, strings, etc.)
            if weight is not None and not isinstance(weight, (int, float)):
                errors["weight"] = "El peso debe ser numérico"

            if height is not None and not isinstance(height, (int, float)):
                errors["height"] = "La altura debe ser numérica"

            for field, value, label in [
                ("waistPerimeter", waistPerimeter, "waistPerimeter"),
                ("armPerimeter", armPerimeter, "armPerimeter"),
                ("legPerimeter", legPerimeter, "legPerimeter"),
                ("calfPerimeter", calfPerimeter, "calfPerimeter"),
            ]:
                if value is not None and not isinstance(value, (int, float)):
                    errors[field] = "Debe ser numérico"

            # 4. Validar rangos antropométricos
            # =========================
            if isinstance(weight, (int, float)):
                if weight <= 0:
                    errors["weight"] = "El peso debe ser mayor a 0"
                elif weight < 0.5 or weight > 500:
                    errors["weight"] = "El peso debe estar entre 0.5 y 500 kg"

            # Altura (incluye recién nacidos)
            if isinstance(height, (int, float)):
                if height <= 0:
                    errors["height"] = "La altura debe ser mayor a 0"
                elif height < 0.3 or height > 2.5:
                    errors["height"] = "La altura debe estar entre 0.3 y 2.5 metros"

            # Perímetro de cintura (cm)
            if waistPerimeter < 0 or waistPerimeter > 200:
                errors["waistPerimeter"] = "Debe estar entre 0 y 200 cm"

            if armPerimeter < 0 or armPerimeter > 80:
                errors["armPerimeter"] = "Debe estar entre 10 y 80 cm"

            if legPerimeter < 0 or legPerimeter > 120:
                errors["legPerimeter"] = "Debe estar entre 20 y 120 cm"

            if calfPerimeter < 0 or calfPerimeter > 70:
                errors["calfPerimeter"] = "Debe estar entre 15 y 70 cm"
            # 5. Retornar errores si existen
            if errors:
                return error_response(
                    msg="Error de validación", errors=errors, code=400
                )

            # 6. Buscar participante
            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()

            if not participant:
                return error_response(
                    msg="Error de validación",
                    errors={"participant_external_id": "Participante no encontrado"},
                    code=400,
                )

            # 7. Calcular IMC
            bmi = self.calculateBMI(weight, height)

            # Clasificación solo para adultos (opcional)
            status = self.classify_bmi_adult(bmi)

            # 8. Crear evaluación
            assessment = Assessment(
                participant_id=participant.id,
                date=date,
                weight=weight,
                height=height,
                waistPerimeter=waistPerimeter,
                bmi=bmi,
                status=status,
                armPerimeter=armPerimeter,
                legPerimeter=legPerimeter,
                calfPerimeter=calfPerimeter,
            )

            db.session.add(assessment)

            log_activity(
                type="MEDICION",
                title="Medición registrada",
                description=f"Se registró una evaluación para {participant.firstName} {participant.lastName}",
            )

            db.session.commit()

            return success_response(
                msg="Evaluación registrada exitosamente",
                data={
                    "external_id": assessment.external_id,
                    "participant_external_id": participant.external_id,
                    "bmi": assessment.bmi,
                    "status": assessment.status,
                },
                code=200,
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
                return error_response(
                    msg="Error de validación",
                    errors={"participant_external_id": "Participante no encontrado"},
                    code=400,
                )

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
                    "armPerimeter": a.armPerimeter,
                    "legPerimeter": a.legPerimeter,
                    "calfPerimeter": a.calfPerimeter,
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
            return error_response(msg=f"Error interno del servidor: {str(e)}", code=500)

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

            return success_response(
                msg="Distribución por estado nutricional", data=chart_data, code=200
            )

        except Exception as e:
            return error_response(msg=f"Error interno del servidor: {str(e)}", code=500)
