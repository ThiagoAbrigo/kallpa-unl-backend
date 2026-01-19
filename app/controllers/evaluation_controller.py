from app.models.evaluation import Evaluation
from app.models.evaluationResult import EvaluationResult
from app.models.participant import Participant
from app.models.test import Test
from app.models.testExercise import TestExercise
from app.utils.responses import error_response, success_response
from app import db
from datetime import datetime


class EvaluationController:

    def list(self):
        try:
            tests = Test.query.filter_by(status="Activo").all()

            result = []
            for test in tests:
                exercises = TestExercise.query.filter_by(test_id=test.id).all()
                exercises_data = [
                    {"external_id": ex.external_id, "name": ex.name, "unit": ex.unit}
                    for ex in exercises
                ]

                result.append(
                    {
                        "external_id": test.external_id,
                        "name": test.name,
                        "description": test.description,
                        "frequency_months": test.frequency_months,
                        "exercises": exercises_data,
                        "status": test.status,
                    }
                )

            return success_response(msg="Listado de tests con ejercicios", data=result)

        except Exception as e:
            return error_response(f"Internal error: {str(e)}", 500)

    def register(self, data):
        try:
            if not isinstance(data, dict):
                return error_response("Datos inválidos", code=400)

            name_input = data.get("name", "").strip() if data.get("name") else ""
            freq_input = data.get("frequency_months")
            description_input = (
                data.get("description", "").strip() if data.get("description") else None
            )
            exercises_input = data.get("exercises", [])

            name_normalized = name_input.lower()

            validation_errors = {}

            if not name_input:
                validation_errors["name"] = "Campo requerido"
            elif Test.query.filter(db.func.lower(Test.name) == name_normalized).first():
                validation_errors["name"] = "El test con ese nombre ya existe"

            if freq_input is None:
                validation_errors["frequency_months"] = "Campo requerido"
            elif not isinstance(freq_input, int):
                validation_errors["frequency_months"] = (
                    "La frecuencia debe ser un número entero"
                )
            elif freq_input < 1 or freq_input > 12:
                validation_errors["frequency_months"] = (
                    "La frecuencia debe estar entre 1 y 12 meses"
                )

            if not exercises_input:
                validation_errors["exercises"] = "Se requiere al menos un ejercicio"
            else:
                for i, ex in enumerate(exercises_input):
                    ex_name = ex.get("name", "").strip() if ex.get("name") else ""
                    ex_unit = ex.get("unit", "").strip() if ex.get("unit") else ""

                    if not ex_name:
                        validation_errors[f"exercises[{i}].name"] = "Campo requerido"
                    if not ex_unit:
                        validation_errors[f"exercises[{i}].unit"] = "Campo requerido"

            if validation_errors:
                error_data = {
                    "test_external_id": None,
                    "name": name_input if name_input else None,
                    "frequency_months": freq_input,
                    "description": description_input,
                    "exercises": (
                        [
                            {
                                "name": (
                                    ex.get("name", "").strip()
                                    if ex.get("name")
                                    else None
                                ),
                                "unit": (
                                    ex.get("unit", "").strip()
                                    if ex.get("unit")
                                    else None
                                ),
                            }
                            for ex in exercises_input
                        ]
                        if exercises_input
                        else []
                    ),
                    "validation_errors": validation_errors,
                }
                return error_response(
                    msg="Error de validación", data=error_data, code=400
                )

            test = Test(
                name=name_normalized,
                description=description_input,
                frequency_months=freq_input,
            )
            db.session.add(test)
            db.session.flush()

            exercises_created = []
            for ex in exercises_input:
                exercise = TestExercise(
                    test_id=test.id,
                    name=ex.get("name").strip(),
                    unit=ex.get("unit").strip(),
                )
                db.session.add(exercise)
                exercises_created.append(
                    {
                        "name": exercise.name,
                        "unit": exercise.unit,
                    }
                )

            db.session.commit()

            success_data = {
                "test_external_id": test.external_id,
                "name": test.name,
                "frequency_months": test.frequency_months,
                "description": test.description,
                "exercises": exercises_created,
            }

            return success_response(
                msg="Test creado correctamente", data=success_data, code=200
            )

        except Exception as e:
            db.session.rollback()
            return error_response(msg="Error interno del servidor", data=None, code=500)

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

            test = Test.query.filter_by(external_id=data["test_external_id"]).first()

            if not test:
                return error_response("Test no encontrado")

            results = data.get("results", [])
            if not any(
                isinstance(r.get("value"), (int, float)) and r.get("value") > 0
                for r in results
            ):
                return error_response(
                    "Debe ingresar al menos un valor válido para los ejercicios"
                )

            date_str = data.get("date")
            if date_str:
                try:
                    evaluation_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    return error_response(
                        "Formato de fecha inválido, debe ser YYYY-MM-DD"
                    )
            else:
                evaluation_date = None

            evaluation = Evaluation(
                participant_id=participant.id,
                test_id=test.id,
                date=evaluation_date,
                general_observations=data.get("general_observations"),
            )

            db.session.add(evaluation)
            db.session.flush()

            valid_exercises = {
                ex.external_id: ex.id
                for ex in TestExercise.query.filter_by(test_id=test.id).all()
            }

            used = set()

            for r in results:
                ex_id = valid_exercises.get(r.get("test_exercise_external_id"))

                if not ex_id:
                    return error_response("Ejercicio no pertenece al test")

                if ex_id in used:
                    return error_response("Ejercicio duplicado")

                used.add(ex_id)

                value = r.get("value")
                if value is None:
                    return error_response("Debe ingresar un valor para cada ejercicio")

                if not isinstance(value, (int, float)) or value <= 0:
                    return error_response(
                        "Debe ingresar un valor mayor que 0 para cada ejercicio"
                    )

                db.session.add(
                    EvaluationResult(
                        evaluation_id=evaluation.id,
                        test_exercise_id=ex_id,
                        value=value,
                    )
                )

            db.session.commit()

            return success_response(
                msg="Test aplicado correctamente",
                data={"evaluation_external_id": evaluation.external_id},
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}", 500)

    def get_participant_progress(self, participant_external_id):
        try:
            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()

            if not participant:
                return error_response("Participante no encontrado")

            evaluations = (
                Evaluation.query.filter_by(participant_id=participant.id)
                .order_by(Evaluation.date.asc())
                .all()
            )

            progress_data = []

            for eval in evaluations:
                results = EvaluationResult.query.filter_by(evaluation_id=eval.id).all()

                result_dict = {r.exercise.name: r.value for r in results}

                total = sum(result_dict.values()) if result_dict else 0

                progress_data.append(
                    {
                        "evaluation_external_id": eval.external_id,
                        "date": eval.date.strftime("%Y-%m-%d") if eval.date else None,
                        "test_name": eval.test.name,  # 👈 AQUÍ
                        "results": result_dict,
                        "total": total,
                        "general_observations": eval.general_observations,
                    }
                )

            return success_response(
                msg="Progreso obtenido correctamente",
                data={
                    "participant_name": participant.firstName,
                    "progress": progress_data,
                },
            )

        except Exception as e:
            return error_response(f"Internal error: {str(e)}", 500)

    def list_tests_for_participant(self, participant_external_id):
        try:
            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()
            if not participant:
                return error_response("Participante no encontrado", 404)

            tests = Test.query.filter_by(status="Activo").all()

            result = []
            for test in tests:
                exercises = TestExercise.query.filter_by(test_id=test.id).all()
                exercises_data = [
                    {"external_id": ex.external_id, "name": ex.name, "unit": ex.unit}
                    for ex in exercises
                ]

                evaluation = Evaluation.query.filter_by(
                    participant_id=participant.id, test_id=test.id
                ).first()

                result.append(
                    {
                        "external_id": test.external_id,
                        "name": test.name,
                        "description": test.description,
                        "frequency_months": test.frequency_months,
                        "exercises": exercises_data,
                        "already_done": bool(evaluation),
                        "done_date": (
                            evaluation.date.strftime("%Y-%m-%d") if evaluation else None
                        ),
                    }
                )

            return success_response(
                msg="Listado de tests para el participante", data=result
            )

        except Exception as e:
            return error_response(f"Internal error: {str(e)}", 500)

    def get_by_external_id(self, external_id):
        try:
            test = Test.query.filter_by(external_id=external_id).first()
            if not test:
                return error_response("Test no encontrado", 404)

            exercises = TestExercise.query.filter_by(test_id=test.id).all()
            exercises_data = [{"name": ex.name, "unit": ex.unit} for ex in exercises]

            data = {
                "external_id": test.external_id,
                "name": test.name,
                "description": test.description,
                "frequency_months": test.frequency_months,
                "exercises": exercises_data,
                "status": test.status,
            }

            return success_response(msg="Detalle del test obtenido", data=data)
        except Exception as e:
            return error_response(f"Error al obtener test: {str(e)}", 500)
