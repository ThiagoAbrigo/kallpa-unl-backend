from app.utils.responses import success_response, error_response
from app import db
from app.models.test import Test
from app.models.testExercise import TestExercise
from app.models.evaluation import Evaluation
from app.models.participant import Participant
from app.models.evaluationResult import EvaluationResult

from datetime import date


class EvaluationServiceDB:

    def register_test(self, data):
        try:
            test = Test(
                name=data["name"],
                description=data.get("description"),
                frequency_months=data["frequency_months"],
            )

            db.session.add(test)
            db.session.flush()

            for ex in data["exercises"]:
                exercise = TestExercise(
                    test_id=test.id, name=ex["name"], unit=ex["unit"]
                )
                db.session.add(exercise)

            db.session.commit()
            return success_response(
                msg="Test creado correctamente",
                data={"test_external_id": test.external_id},
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}")

    def apply_test(self, data):
        try:
            participant = Participant.query.filter_by(
                external_id=data["participant_external_id"]
            ).first()
            if not participant:
                return error_response("Participant not found")

            test = Test.query.filter_by(
                external_id=data["test_external_id"]
            ).first()
            if not test:
                return error_response("Test not found")

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

            for res in data["results"]:
                exercise_id = valid_exercises.get(
                    res.get("test_exercise_external_id")
                )

                if not exercise_id:
                    return error_response(
                        "Exercise does not belong to this test"
                    )

                result = EvaluationResult(
                    evaluation_id=evaluation.id,
                    test_exercise_id=exercise_id,
                    value=res["value"],
                    observation=res.get("observation"),
                )
                db.session.add(result)

            db.session.commit()

            return success_response(
                msg="Test aplicado correctamente",
                data={"evaluation_external_id": evaluation.external_id},
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}")