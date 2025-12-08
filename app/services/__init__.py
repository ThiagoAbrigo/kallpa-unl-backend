import os

# USERS
from app.services.users.user_service_mock import UserServiceMock
from app.services.users.user_service_db import UserServiceDB

# ATTENDANCE
from app.services.attendance.attendance_service_mock import AttendanceServiceMock
from app.services.attendance.attendance_service_db import AttendanceServiceDB

# Get USE_MOCK from environment variable
USE_MOCK = os.getenv('USE_MOCK', 'false').lower() == 'true'

if USE_MOCK:
    user_service = UserServiceMock()
    attendance_service = AttendanceServiceMock()
else:
    user_service = UserServiceDB()
    attendance_service = AttendanceServiceDB()
