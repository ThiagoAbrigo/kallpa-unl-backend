from app.utils.responses import success_response, error_response
from app import db
from app.models.test import Test
from app.models.testExercise import TestExercise
from app.models.evaluation import Evaluation
from app.models.participant import Participant
from app.models.evaluationResult import EvaluationResult
from datetime import date, timedelta
import calendar
from datetime import datetime


class EvaluationServiceDB:

    # LISTAR TESTS
    def list_tests(self):
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
                    }
                )

            return success_response(msg="Listado de tests con ejercicios", data=result)

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

            if (
                not isinstance(data["frequency_months"], int)
                or data["frequency_months"] <= 0
            ):
                return error_response(
                    "La frecuencia debe ser un número entero positivo"
                )

            if (
                "exercises" not in data
                or not isinstance(data["exercises"], list)
                or len(data["exercises"]) == 0
            ):
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
                db.session.add(
                    TestExercise(
                        test_id=test.id,
                        name=ex["name"].strip(),
                        unit=ex["unit"].strip(),
                    )
                )

            db.session.commit()

            return success_response(
                msg="Test creado correctamente",
                data={"test_external_id": test.external_id},
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

            test = Test.query.filter_by(external_id=data["test_external_id"]).first()

            if not test:
                return error_response("Test no encontrado")

            if (
                "results" not in data
                or not isinstance(data["results"], list)
                or len(data["results"]) == 0
            ):
                return error_response("Debe ingresar resultados")

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

            for r in data["results"]:
                ex_id = valid_exercises.get(r.get("test_exercise_external_id"))

                if not ex_id:
                    return error_response("Ejercicio no pertenece al test")

                if ex_id in used:
                    return error_response("Ejercicio duplicado")

                used.add(ex_id)

                db.session.add(
                    EvaluationResult(
                        evaluation_id=evaluation.id,
                        test_exercise_id=ex_id,
                        value=r.get("value"),
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

    # HISTORIAL / COMPARACIÓN
    def get_history(
        self,
        participant_external_id,
        test_external_id,
        months=6,
    ):
        try:
            # -------------------------
            # Validaciones básicas
            # -------------------------
            if not participant_external_id:
                return error_response("Debe seleccionar un participante", 400)

            if not test_external_id:
                return error_response("Debe seleccionar un test", 400)

            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()

            if not participant:
                return error_response("Participante no encontrado", 404)

            test = Test.query.filter_by(external_id=test_external_id).first()

            if not test:
                return error_response("Test no encontrado", 404)

            # -------------------------
            # Validar periodo permitido
            # -------------------------
            try:
                months = int(months)
            except Exception:
                months = 6

            if months not in [3, 6, 9, 12]:
                months = 6

            end_date = date.today()
            start_date = end_date - timedelta(days=months * 30)

            # -------------------------
            # Obtener evaluaciones
            # -------------------------
            N = 2
            evaluations = (
                Evaluation.query.filter(
                    Evaluation.participant_id == participant.id,
                    Evaluation.test_id == test.id,
                )
                .order_by(Evaluation.date.desc())
                .limit(N)
                .all()
            )

            evaluations.reverse() 

            if not evaluations:
                return success_response(
                    msg="No hay evaluaciones en el periodo seleccionado",
                    data={
                        "participant_external_id": participant_external_id,
                        "test_external_id": test_external_id,
                        "months": months,
                        "exercises": {},
                    },
                )

            # -------------------------
            # Construir historial
            # -------------------------
            history = {}

            for ev in evaluations:
                for r in ev.results:
                    if not r.exercise:
                        continue

                    ex_id = r.exercise.external_id

                    if ex_id not in history:
                        history[ex_id] = {
                            "exercise_name": r.exercise.name,
                            "unit": r.exercise.unit,
                            "timeline": [],
                        }

                    history[ex_id]["timeline"].append(
                        {
                            "date": ev.date.isoformat(),
                            "value": r.value,
                        }
                    )

            # -------------------------
            # Estadísticas y tendencia
            # -------------------------
            for ex in history.values():
                values = [p["value"] for p in ex["timeline"]]

                if len(values) < 2:
                    ex["stats"] = {
                        "count": len(values),
                        "average": values[0] if values else None,
                        "min": values[0] if values else None,
                        "max": values[0] if values else None,
                        "first_value": values[0] if values else None,
                        "last_value": values[0] if values else None,
                        "delta": None,
                    }

                    ex["trend"] = {
                        "status": "Datos insuficientes",
                        "description": "Se requiere al menos 2 evaluaciones para comparar",
                    }
                    continue

                first = values[0]
                last = values[-1]
                delta = round(last - first, 2)

                if delta > 0:
                    trend_status = "Mejorando"
                elif delta < 0:
                    trend_status = "Disminuyendo"
                else:
                    trend_status = "Estable"

                ex["stats"] = {
                    "count": len(values),
                    "average": round(sum(values) / len(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "first_value": first,
                    "last_value": last,
                    "delta": delta,
                }

                ex["trend"] = {
                    "status": trend_status,
                    "description": f"Inicio: {first} → Fin: {last} ({delta})",
                }

            # -------------------------
            # Respuesta final
            # -------------------------
            return success_response(
                msg="Historial de test obtenido correctamente",
                data={
                    "participant_external_id": participant_external_id,
                    "test_external_id": test_external_id,
                    "months": months,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "exercises": history,
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

                # Verificar si el participante ya hizo este test
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
