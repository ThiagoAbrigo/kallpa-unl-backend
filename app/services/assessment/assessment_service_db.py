from app.models.participant import Participant
from app.models.assessment import Assessment
from app.utils.responses import success_response, error_response
from app import db


class AssessmentServiceDB:
    def calculateBMI(self, weight, height):
        if height and height > 0:
            return round(weight / (height ** 2), 2)
        return 0

    def register_evaluation(self, data):
        try:
            participant_external_id = data.get("participant_external_id")

            participant = Participant.query.filter_by(
                external_id=participant_external_id
            ).first()

            if not participant:
                return error_response("Participant not found")

            bmi = self.calculateBMI(
                data.get("weight"),
                data.get("height")
            )
            assessment = Assessment(
                participant_id=participant.id,
                date=data.get("date"),
                weight=data.get("weight"),
                height=data.get("height"),
                waistPerimeter=data.get("waistPerimeter"),
                wingspan=data.get("wingspan"),
                bmi=bmi
            )

            db.session.add(assessment)
            db.session.commit()

            return success_response(
                msg="Assessment registered successfully",
                data={
                    "external_id": assessment.external_id,
                    "participant_external_id": participant.external_id,
                    "bmi": assessment.bmi,
                },
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}")
