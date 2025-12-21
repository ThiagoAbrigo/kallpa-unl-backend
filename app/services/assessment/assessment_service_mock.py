import json
import os
from app.utils.responses import success_response, error_response
import uuid

class AssessmentServiceMock:

    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.mock_path = os.path.join(base, "mock", "assessment.json")

        if not os.path.exists(self.mock_path):
            with open(self.mock_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    def _load(self):
        with open(self.mock_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.mock_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def calculateBMI(self, weight, height):
        if height and height > 0:
            return round(weight / (height**2), 2)
        return 0

    def register_evaluation(self, data):
        try:
            assessments = self._load()

            bmi = self.calculateBMI(
                data.get("weight"),
                data.get("height")
            )

            assessment = {
                "external_id": str(uuid.uuid4()),
                "participant_external_id": data.get("participant_external_id"),
                "date": data.get("date"),
                "weight": data.get("weight"),
                "height": data.get("height"),
                "waistPerimeter": data.get("waistPerimeter"),
                "wingspan": data.get("wingspan"),
                "bmi": bmi
            }

            assessments.append(assessment)
            self._save(assessments)

            return success_response(
                msg="Assessment registered successfully (MOCK)",
                data=assessment
            )

        except Exception as e:
            return error_response(f"Internal error MOCK: {str(e)}")
