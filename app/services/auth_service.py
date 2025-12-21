import requests
from app.config.config import Config
from app.utils.responses import error_response
from app.utils.jwt import generate_token


class AuthService:
    def login(self, data):
        email = data.get("email", "").lower().strip()
        password = data.get("password")

        # BYPASS
        if email == "dev@kallpa.com":
            user_data = {
                "external_id": "usuario-mock-bypass",
                "email": email,
                "rol": "admin",
                "nombre": "Admin",
                "apellido": "Bypass",
            }

            token = generate_token(
                {
                    "sub": user_data["external_id"],
                    "email": user_data["email"],
                    "rol": user_data["rol"],
                }
            )

            return {
                "status": "ok",
                "msg": "Login MOCK",
                "token": token,
                "user": user_data,
                "code": 200,
            }

        # DOCKER REAL
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

            return error_response("Credenciales inválidas")

        except Exception:
            return error_response("No se pudo conectar al sistema externo", 500)
