import json
import os
from app.utils.responses import success_response, error_response
import uuid
from datetime import date


class EvaluationServiceMock:

    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.test_path = os.path.join(base, "mock", "tests.json")
        self.evaluation_path = os.path.join(base, "mock", "evaluations.json")

        for path in [self.test_path, self.evaluation_path]:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)

    def _load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def register_test(self, data):
        try:
            tests = self._load(self.test_path)

            test_external_id = str(uuid.uuid4())

            test = {
                "external_id": test_external_id,
                "name": data["name"],
                "description": data.get("description"),
                "frequency_months": data["frequency_months"],
                "exercises": [],
            }

            for ex in data["exercises"]:
                test["exercises"].append(
                    {
                        "external_id": str(uuid.uuid4()),
                        "name": ex["name"],
                        "unit": ex["unit"],
                    }
                )

            tests.append(test)
            self._save(self.test_path, tests)

            return success_response(
                msg="Test creado correctamente (MOCK)",
                data={"test_external_id": test_external_id},
            )

        except Exception as e:
            return error_response(f"Internal error MOCK: {str(e)}")

    def apply_test(self, data):
        try:
            tests = self._load(self.test_path)
            evaluations = self._load(self.evaluation_path)

            test = next(
                (t for t in tests if t["external_id"] == data["test_external_id"]), None
            )
            if not test:
                return error_response("Test not found (MOCK)")

            evaluation_external_id = str(uuid.uuid4())

            valid_exercises = {ex["external_id"]: ex for ex in test["exercises"]}

            results = []
            for res in data["results"]:
                exercise = valid_exercises.get(res["test_exercise_external_id"])

                if not exercise:
                    return error_response(
                        "Exercise does not belong to this test (MOCK)"
                    )

                results.append(
                    {
                        "exercise_external_id": exercise["external_id"],
                        "exercise_name": exercise["name"],
                        "value": res["value"],
                        "observation": res.get("observation"),
                    }
                )

            evaluation = {
                "external_id": evaluation_external_id,
                "participant_external_id": data["participant_external_id"],
                "test_external_id": test["external_id"],
                "date": date.today().isoformat(),
                "general_observations": data.get("general_observations"),
                "results": results,
            }

            evaluations.append(evaluation)
            self._save(self.evaluation_path, evaluations)

            return success_response(
                msg="Test aplicado correctamente (MOCK)",
                data={"evaluation_external_id": evaluation_external_id},
            )

        except Exception as e:
            return error_response(f"Internal error MOCK: {str(e)}")