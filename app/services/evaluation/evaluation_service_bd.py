from app.utils.responses import success_response, error_response
from app import db
from app.models.test import Test
from app.models.testExercise import TestExercise
from app.models.evaluation import Evaluation
from app.models.participant import Participant
from app.models.evaluationResult import EvaluationResult
from datetime import date
import calendar


class EvaluationServiceDB:

    # LISTAR TESTS
    def list_tests(self):
        try:
            tests = Test.query.filter_by(status="Activo").all()

            result = []
            for test in tests:
                exercises = TestExercise.query.filter_by(test_id=test.id).all()
                exercises_data = [
                    {
                        "external_id": ex.external_id,
                        "name": ex.name,
                        "unit": ex.unit
                    } for ex in exercises
                ]

                result.append({
                    "external_id": test.external_id,
                    "name": test.name,
                    "description": test.description,
                    "frequency_months": test.frequency_months,
                    "exercises": exercises_data
                })

            return success_response(
                msg="Listado de tests con ejercicios",
                data=result
            )

        except Exception as e:
            return error_response(f"Internal error: {str(e)}", 500)

    
    # REGISTRAR TEST
    def register_test(self, data):
        try:
            if not data or not isinstance(data, dict):
                return error_response("Datos inválidos")

            if "name" not in data or not data["name"].strip():
                return error_response("Por favor ingrese el nombre del test")

            if Test.query.filter_by(name=data["name"].strip()).first():
                return error_response("El test con ese nombre ya existe")

            if "frequency_months" not in data:
                return error_response("Se requiere la frecuencia en meses")

            if not isinstance(data["frequency_months"], int) or data["frequency_months"] <= 0:
                return error_response("La frecuencia debe ser un número entero positivo")

            if "exercises" not in data or not isinstance(data["exercises"], list) or len(data["exercises"]) == 0:
                return error_response("Debe ingresar al menos un ejercicio")

            exercise_names = set()

            for ex in data["exercises"]:
                if not ex.get("name") or not ex.get("unit"):
                    return error_response("Cada ejercicio debe tener nombre y unidad")

                key = ex["name"].strip().lower()
                if key in exercise_names:
                    return error_response("Ejercicio repetido")

                exercise_names.add(key)

            test = Test(
                name=data["name"].strip(),
                description=data.get("description"),
                frequency_months=data["frequency_months"],
            )

            db.session.add(test)
            db.session.flush()

            for ex in data["exercises"]:
                db.session.add(TestExercise(
                    test_id=test.id,
                    name=ex["name"].strip(),
                    unit=ex["unit"].strip()
                ))

            db.session.commit()

            return success_response(
                msg="Test creado correctamente",
                data={"test_external_id": test.external_id}
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}", 500)

    # APLICAR TEST
    def apply_test(self, data):
        try:
            if not data or not isinstance(data, dict):
                return error_response("Datos inválidos")

            if "participant_external_id" not in data:
                return error_response("Debe seleccionar un participante")

            if "test_external_id" not in data:
                return error_response("Debe seleccionar un test")

            participant = Participant.query.filter_by(
                external_id=data["participant_external_id"]
            ).first()

            if not participant:
                return error_response("Participante no encontrado")

            test = Test.query.filter_by(
                external_id=data["test_external_id"]
            ).first()

            if not test:
                return error_response("Test no encontrado")

            if "results" not in data or not isinstance(data["results"], list) or len(data["results"]) == 0:
                return error_response("Debe ingresar resultados")

            evaluation = Evaluation(
                participant_id=participant.id,
                test_id=test.id,
                date=date.today(),
                general_observations=data.get("general_observations"),
            )

            db.session.add(evaluation)
            db.session.flush()

            valid_exercises = {
                ex.external_id: ex.id
                for ex in TestExercise.query.filter_by(test_id=test.id).all()
            }

            used = set()

            for r in data["results"]:
                ex_id = valid_exercises.get(r.get("test_exercise_external_id"))

                if not ex_id:
                    return error_response("Ejercicio no pertenece al test")

                if ex_id in used:
                    return error_response("Ejercicio duplicado")

                used.add(ex_id)

                db.session.add(EvaluationResult(
                    evaluation_id=evaluation.id,
                    test_exercise_id=ex_id,
                    value=r.get("value")
                ))

            db.session.commit()

            return success_response(
                msg="Test aplicado correctamente",
                data={"evaluation_external_id": evaluation.external_id}
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}", 500)

    
    # HISTORIAL / COMPARACIÓN
    def get_history(self, participant_external_id, test_external_id, months=6):
        try:
            if not participant_external_id:
                return error_response("Debe seleccionar un participante", 400)

            if not test_external_id:
                return error_response("Debe seleccionar un test", 400)

            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()

            if not participant:
                return error_response("Participante no encontrado", 404)

            test = Test.query.filter_by(
                external_id=test_external_id
            ).first()

            if not test:
                return error_response("Test no encontrado", 404)

            try:
                months = int(months)
            except Exception:
                months = 6

            if months <= 0:
                months = 6

            today = date.today()
            year = today.year
            month = today.month - months

            while month <= 0:
                month += 12
                year -= 1

            day = min(today.day, calendar.monthrange(year, month)[1])
            cutoff = date(year, month, day)

            evaluations = Evaluation.query.filter(
                Evaluation.participant_id == participant.id,
                Evaluation.test_id == test.id,
                Evaluation.date >= cutoff
            ).order_by(Evaluation.date.asc()).all()

            trends = {}

            for ev in evaluations:
                for r in ev.results:
                    if not r.exercise:
                        continue

                    ex_id = r.exercise.external_id
                    ex_name = r.exercise.name

                    trends.setdefault(ex_id, {
                        "exercise_name": ex_name,
                        "values": []
                    })["values"].append(r.value)

            comparison = {}

            for ex_id, info in trends.items():
                values = info["values"]

                average = round(sum(values) / len(values), 2)
                delta = None
                status = "Sin datos suficientes"

                if len(values) >= 2:
                    delta = round(values[-1] - values[0], 2)

                    if delta > 0:
                        status = "Está avanzando bien"
                    elif delta < 0:
                        status = "Está bajando el rendimiento"
                    else:
                        status = "Sigue igual"

                comparison[ex_id] = {
                    "exercise_name": info["exercise_name"],
                    "average": average,
                    "delta": delta,
                    "status": status
                }

            return success_response(
                msg="Seguimiento del test obtenido correctamente",
                data={
                    "participant_external_id": participant_external_id,
                    "test_external_id": test_external_id,
                    "comparison": comparison
                }
            )

        except Exception as e:
            return error_response(f"Internal error: {str(e)}", 500)
