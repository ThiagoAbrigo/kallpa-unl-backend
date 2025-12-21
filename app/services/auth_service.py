import requests
import jwt
import datetime
from flask import current_app
from app.config.config import Config


class AuthService:
    def login(self, data):
        email = data.get("email", "").lower().strip()  # Importante: minúsculas
        password = data.get("password")

        # ---------------------------------------------------------
        # 1. CAMINO DE EMERGENCIA (BYPASS / MOCK)
        # ---------------------------------------------------------
        # Si usas este correo, entras SIEMPRE, funcione o no el Docker.
        if email == "dev@kallpa.com":
            user_data = {
                "id": 1,
                "external_id": "usuario-mock-bypass",
                "email": "dev@kallpa.com",
                "rol": "admin",
                "nombre": "Admin", 
                "apellido": "Bypass"
            }
            token = self._generate_token(user_data)
            return {
                "status": "ok",
                "msg": "Login MOCK (Bypass activado)",
                "token": token,
                "user": user_data,
                "origen": "local_bypass"
            }, 200

        # ---------------------------------------------------------
        # 2. CAMINO REAL (DOCKER DEL PROFESOR)
        # ---------------------------------------------------------
        try:
            # Usamos la variable que definimos en Config
            external_url = f"{Config.PERSON_API_URL}/login"
            payload = {"email": email, "password": password}
            
            # Timeout de 3 seg para que no se cuelgue si el Docker está apagado
            response = requests.post(external_url, json=payload, timeout=3)
            
            if response.status_code == 200:
                resp_json = response.json()
                
                # El API del profe devuelve la data dentro de "data"
                real_user_data = resp_json.get("data", {})
                
                # OBTENER EL TOKEN REAL DEL DOCKER
                token_real = real_user_data.get("token")
                
                return {
                    "status": "ok", 
                    "msg": "Login Exitoso (Vía Docker)",
                    "token": token_real,  # <--- Usamos el token oficial
                    "user": real_user_data,
                    "origen": "docker_real"
                }, 200
            else:
                return {
                    "status": "error", 
                    "msg": response.json().get("message", "Credenciales inválidas en Docker")
                }, 401

        except Exception as e:
            # Si el Docker está apagado o falla, te avisa pero no explota
            return {
                "status": "error", 
                "msg": f"No se pudo conectar al sistema externo: {str(e)}"
            }, 500

    def _generate_token(self, user_data):
        """Genera un token firmado con la clave secreta de Flask"""
        payload = {
            "sub": user_data.get("external_id") or user_data.get("id"),
            "email": user_data.get("email"),
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        return jwt.encode(payload, current_app.config.get("JWT_SECRET_KEY"), algorithm="HS256")
