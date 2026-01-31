# app/utils/jwt_required.py
import jwt
from functools import wraps
from flask import request, jsonify, current_app

SESSION_ERROR_MSG = "Tu sesión ha terminado por seguridad. Por favor, vuelve a iniciar sesión para continuar con tus actividades."

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
            return jsonify({
                "msg": "No hay sesión activa. Por favor inicia sesión.",
                "code": 401
            }), 401

        try:
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({
                    "msg": SESSION_ERROR_MSG,
                    "code": 401
                }), 401
            
            token = parts[1]
            
            if token.count('.') == 2:
                data = jwt.decode(
                    token,
                    current_app.config["JWT_SECRET_KEY"],
                    algorithms=["HS256"]
                )
                request.user = data
            else:
                from app.models.user import User
                user = User.query.filter_by(java_token=f"Bearer {token}").first()
                if not user:
                    user = User.query.filter_by(java_token=token).first()
                
                if not user:
                    return jsonify({
                        "msg": SESSION_ERROR_MSG,
                        "code": 401
                    }), 401
                
                request.user = {
                        'sub': user.external_id,
                        'email': user.email,
                        'role': user.role,
                        'external_id': user.external_id
                    }

        except jwt.ExpiredSignatureError:
            return jsonify({
                "msg": SESSION_ERROR_MSG,
                "code": 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "msg": SESSION_ERROR_MSG,
                "code": 401
            }), 401
        except Exception:
            return jsonify({
                "msg": SESSION_ERROR_MSG,
                "code": 401
            }), 401

        return f(*args, **kwargs)

    return decorated
