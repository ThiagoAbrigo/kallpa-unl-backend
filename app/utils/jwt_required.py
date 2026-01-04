# app/utils/jwt_required.py
import jwt
from functools import wraps
from flask import request, jsonify


def get_jwt_identity():
    """Obtiene el external_id del usuario del token JWT decodificado."""
    user_data = getattr(request, 'user', None)
    if user_data:
        return user_data.get('sub') or user_data.get('external_id') or user_data.get('external') or user_data.get('id')
    return None


def jwt_required(f):
    """
    Decorador que valida la presencia de un token JWT en el header Authorization.
    Acepta tokens generados por Python (JWT) y por Java (Bearer token).
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
            
            if token.count('.') == 2:
                data = jwt.decode(token, options={"verify_signature": False})
                request.user = data
            else:
                from app.models.user import User
                user = User.query.filter_by(java_token=f"Bearer {token}").first()
                if not user:
                    user = User.query.filter_by(java_token=token).first()
                
                if user:
                    request.user = {
                        'sub': user.external_id,
                        'email': user.email,
                        'role': user.role,
                        'external_id': user.external_id
                    }
                else:
                    return jsonify({"msg": "Invalid Java token", "code": 401}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token has expired", "code": 401}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token", "code": 401}), 401
        except Exception as e:
            return jsonify({"msg": str(e), "code": 401}), 401

        return f(*args, **kwargs)

    return decorated
