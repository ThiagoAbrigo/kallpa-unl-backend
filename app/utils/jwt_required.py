# app/utils/jwt_required.py
import jwt
from functools import wraps
from flask import request, jsonify


def jwt_required(f):
    """
    Decorador que valida la presencia de un token JWT en el header Authorization.
    Acepta tokens generados por el microservicio de usuarios sin verificar la firma.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"msg": "Token is missing", "code": 401}), 401

        try:
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({"msg": "Authorization header must be Bearer token", "code": 401}), 401
            
            token = parts[1]
            data = jwt.decode(token, options={"verify_signature": False})
            request.user = data

        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token has expired", "code": 401}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token", "code": 401}), 401
        except Exception as e:
            return jsonify({"msg": str(e), "code": 401}), 401

        return f(*args, **kwargs)

    return decorated
