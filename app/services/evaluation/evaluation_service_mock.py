import json
import os
from app.utils.responses import success_response, error_response
import uuid
from datetime import date
import calendar


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

    def get_history(self, participant_external_id, test_external_id=None, months=6):
        try:
            evaluations = self._load(self.evaluation_path)

            try:
                months = int(months) if months else 6
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

            filtered = []
            for ev in evaluations:
                if ev.get("participant_external_id") != participant_external_id:
                    continue
                if test_external_id and ev.get("test_external_id") != test_external_id:
                    continue
                ev_date = date.fromisoformat(ev.get("date"))
                if ev_date < cutoff:
                    continue
                filtered.append(ev)

            # ordenar por fecha asc
            filtered.sort(key=lambda e: e.get("date"))

            evaluations_data = []
            trends = {}
            for ev in filtered:
                ev_results = []
                for r in ev.get("results", []):
                    ex_id = r.get("exercise_external_id")
                    ex_name = r.get("exercise_name")
                    value = r.get("value")

                    ev_results.append({
                        "exercise_external_id": ex_id,
                        "exercise_name": ex_name,
                        "value": value,
                        "observation": r.get("observation"),
                    })

                    lst = trends.setdefault(ex_id, {"name": ex_name, "values": [], "dates": []})
                    lst["values"].append(value)
                    lst["dates"].append(ev.get("date"))

                evaluations_data.append({
                    "evaluation_external_id": ev.get("external_id"),
                    "date": ev.get("date"),
                    "test_external_id": ev.get("test_external_id"),
                    "general_observations": ev.get("general_observations"),
                    "results": ev_results,
                })

            summary = {"exercise_trends": {}}
            for ex_id, info in trends.items():
                values = info.get("values", [])
                delta = round(values[-1] - values[0], 2) if len(values) >= 2 else None
                avg = round(sum(values) / len(values), 2) if values else None
                summary["exercise_trends"][ex_id] = {
                    "name": info.get("name"),
                    "values": values,
                    "dates": info.get("dates"),
                    "delta": delta,
                    "average": avg,
                }

            return success_response(
                msg="Historial obtenido (MOCK)",
                data={
                    "participant_external_id": participant_external_id,
                    "test_external_id": test_external_id,
                    "period_months": months,
                    "evaluations": evaluations_data,
                    "summary": summary,
                },
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