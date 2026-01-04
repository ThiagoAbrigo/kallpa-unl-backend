import os
from os import path

# USERS
from app.services.users.user_service_mock import UserServiceMock
from app.services.users.user_service_db import UserServiceDB

# ATTENDANCE
from app.services.attendance.attendance_service_mock import AttendanceServiceMock
from app.services.attendance.attendance_service_db import AttendanceServiceDB

# ASSESSMENT
from app.services.assessment.assessment_service_mock import AssessmentServiceMock
from app.services.assessment.assessment_service_db import AssessmentServiceDB

# TEST
from app.services.evaluation.evaluation_service_mock import EvaluationServiceMock
from app.services.evaluation.evaluation_service_bd import EvaluationServiceDB

# Get USE_MOCK from environment variable
USE_MOCK = os.getenv('USE_MOCK', 'false').lower() == 'true'
print(f"[Services] USE_MOCK = {USE_MOCK}")

if USE_MOCK:
    user_service = UserServiceMock()
    attendance_service = AttendanceServiceMock()
    assessment_service = AssessmentServiceMock()
    evaluation_service = EvaluationServiceMock()
else:
    user_service = UserServiceDB()
    attendance_service = AttendanceServiceDB()
    assessment_service = AssessmentServiceDB()
    evaluation_service = EvaluationServiceDB()
