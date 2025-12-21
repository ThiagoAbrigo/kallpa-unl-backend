# app/utils/jwt_required.py
import jwt
from functools import wraps
from flask import request, jsonify, current_app


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return (
                jsonify({"status": "error", "msg": "Token requerido", "code": 401}),
                401,
            )

        try:
            token = auth_header.split(" ")[1]  # Bearer TOKEN
            payload = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
            request.user = payload  # info del usuario logueado

        except Exception:
            return (
                jsonify(
                    {"status": "error", "msg": "Token inválido o expirado", "code": 401}
                ),
                401,
            )
            
        return f(*args, **kwargs)

    return decorated
