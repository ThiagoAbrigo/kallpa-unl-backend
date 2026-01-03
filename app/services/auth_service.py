import requests
from app.config.config import Config
from app.utils.responses import error_response
from app.utils.jwt import generate_token
from werkzeug.security import check_password_hash
from app.models.user import User

class AuthService:
    def login(self, data):
        email = data.get("email", "").lower().strip()
        password = data.get("password")

        if not email or not password:
            return error_response("Email y contraseña requeridos", 400)

        # ---------- LOGIN LOCAL ----------
        user = User.query.filter_by(email=email, status="ACTIVO").first()

        if user and check_password_hash(user.password, password):
            token = generate_token(
                {
                    "sub": user.external_id,
                    "email": user.email,
                    "rol": user.role,
                }
            )

            return {
                "status": "ok",
                "msg": "Login exitoso",
                "token": token,
                "user": {
                    "external_id": user.external_id,
                    "email": user.email,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "role": user.role,
                },
                "code": 200,
            }

        # ---------- BYPASS ----------
        if email == "dev@kallpa.com":
            token = generate_token(
                {
                    "sub": "usuario-mock-bypass",
                    "email": email,
                    "rol": "admin",
                }
            )

            return {
                "status": "ok",
                "msg": "Login MOCK",
                "token": token,
                "user": {
                    "external_id": "usuario-mock-bypass",
                    "email": email,
                    "rol": "admin",
                },
                "code": 200,
            }

        # ---------- LOGIN EXTERNO ----------
        try:
            response = requests.post(
                f"{Config.PERSON_API_URL}/login",
                json={"email": email, "password": password},
                timeout=3,
            )

            if response.status_code == 200:
                real_user = response.json().get("data", {})
                return {
                    "status": "ok",
                    "msg": "Login Exitoso (Docker)",
                    "token": real_user.get("token"),
                    "user": real_user,
                    "code": 200,
                }

        except Exception:
            return error_response("No se pudo conectar al sistema externo", 500)

        return error_response("Credenciales inválidas", 401)
    # def login(self, data):
    #     email = data.get("email", "").lower().strip()
    #     password = data.get("password")

    #     # BYPASS
    #     if email == "dev@kallpa.com":
    #         user_data = {
    #             "external_id": "usuario-mock-bypass",
    #             "email": email,
    #             "rol": "admin",
    #             "nombre": "Admin",
    #             "apellido": "Bypass",
    #         }

    #         token = generate_token(
    #             {
    #                 "sub": user_data["external_id"],
    #                 "email": user_data["email"],
    #                 "rol": user_data["rol"],
    #             }
    #         )

    #         return {
    #             "status": "ok",
    #             "msg": "Login MOCK",
    #             "token": token,
    #             "user": user_data,
    #             "code": 200,
    #         }

    #     # DOCKER REAL
    #     try:
    #         response = requests.post(
    #             f"{Config.PERSON_API_URL}/login",
    #             json={"email": email, "password": password},
    #             timeout=3,
    #         )

    #         if response.status_code == 200:
    #             real_user = response.json().get("data", {})

    #             return {
    #                 "status": "ok",
    #                 "msg": "Login Exitoso (Docker)",
    #                 "token": real_user.get("token"),
    #                 "user": real_user,
    #                 "code": 200,
    #             }

    #         return error_response("Credenciales inválidas")

    #     except Exception:
    #         return error_response("No se pudo conectar al sistema externo", 500)
