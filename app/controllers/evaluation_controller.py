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
                    }
                )

            return success_response(msg="Listado de tests con ejercicios", data=result)

        except Exception as e:
            return error_response(f"Internal error: {str(e)}", 500)

    def register(self, data):

        try:
            if not isinstance(data, dict):
                return error_response("Datos inválidos")

            name = data.get("name", "").strip()
            if not name:
                return error_response({"name": "Campo requerido"})

            if Test.query.filter_by(name=name).first():
                return error_response({"name": "El test con ese nombre ya existe"})

            freq = data.get("frequency_months")

            if freq is None:
                return error_response({"frequency_months": "Campo requerido"})

            if not isinstance(freq, int):
                return error_response(
                    {"frequency_months": "La frecuencia debe ser un número entero"}
                )

            if freq < 1 or freq > 12:
                return error_response(
                    {"frequency_months": "La frecuencia debe estar entre 1 y 12 meses"}
                )

            exercises = data.get("exercises", [])
            if not exercises:
                return error_response(
                    {"exercises": "Se requiere al menos un ejercicio"}
                )

            test = Test(
                name=name,
                description=data.get("description"),
                frequency_months=freq,
            )

            db.session.add(test)
            db.session.flush()

            for ex in exercises:
                ex_name = ex.get("name", "").strip()
                unit = ex.get("unit", "").strip()

                if not ex_name or not unit:
                    return error_response(
                        {"exercises": "Complete los campos de los ejercicios"}
                    )

                db.session.add(
                    TestExercise(
                        test_id=test.id,
                        name=ex_name,
                        unit=unit,
                    )
                )

            db.session.commit()

            return success_response(
                msg="Test creado correctamente",
                data={"test_external_id": test.external_id},
            )

        except Exception as e:
            db.session.rollback()
            return error_response("Error interno del servidor", 500)


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
                return error_response("Formato de fecha inválido, debe ser YYYY-MM-DD")
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

    # def history(
    #     self,
    #     participant_external_id,
    #     test_external_id,
    #     months=6,
    # ):
    #     return evaluation_service.get_history(
    #         participant_external_id=participant_external_id,
    #         test_external_id=test_external_id,
    #         months=months,
    #     )

    def history(
        self,
        participant_external_id,
        test_external_id,
        start_date,
        end_date,
    ):
        try:
            # -------------------------
            # Validaciones básicas
            # -------------------------
            if not participant_external_id:
                return error_response("Debe seleccionar un participante", 400)

            if not test_external_id:
                return error_response("Debe seleccionar un test", 400)

            if not start_date or not end_date:
                return error_response("Debe indicar fecha inicio y fecha fin", 400)

            # -------------------------
            # Parsear fechas
            # -------------------------
            try:
                start_date = datetime.fromisoformat(start_date).date()
                end_date = datetime.fromisoformat(end_date).date()
            except ValueError:
                return error_response("Formato de fecha inválido (YYYY-MM-DD)", 400)

            if start_date > end_date:
                return error_response(
                    "La fecha inicio no puede ser mayor a la fecha fin", 400
                )

            # -------------------------
            # Buscar participante y test
            # -------------------------
            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()

            if not participant:
                return error_response("Participante no encontrado", 404)

            test = Test.query.filter_by(external_id=test_external_id).first()

            if not test:
                return error_response("Test no encontrado", 404)

            # -------------------------
            # Obtener evaluaciones (FILTRADO CORRECTO)
            # -------------------------
            evaluations = (
                Evaluation.query.filter(
                    Evaluation.participant_id == participant.id,
                    Evaluation.test_id == test.id,
                    Evaluation.date >= start_date,
                    Evaluation.date <= end_date,
                )
                .order_by(Evaluation.date.asc())
                .all()
            )

            if not evaluations:
                return success_response(
                    msg="No hay evaluaciones en el periodo seleccionado",
                    data={
                        "participant_external_id": participant_external_id,
                        "test_external_id": test_external_id,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
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
                        "description": "Se requieren al menos 2 evaluaciones",
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
