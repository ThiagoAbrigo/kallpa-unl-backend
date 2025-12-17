import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_token(payload, expires_minutes=60):
    payload = payload.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return token