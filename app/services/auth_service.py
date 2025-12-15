import requests
import jwt
import datetime
from flask import current_app
from app.config.config import Config


class AuthService:
    def login(self, data):
        email = data.get("email")
        password = data.get("password")

       
        # BYPASS DE EMERGENCIA (Para desarrollo sin Docker)
      
        if email == "dev@kallpa.com":
            user_data = {
                "id": 1,
                "external_id": "usuario-mock-bypass",
                "email": "dev@kallpa.com",
                "rol": "admin",
                "nombre": "Admin", 
                "apellido": "Desarrollador"
            }
            token = self._generate_token(user_data)
            
            return {
                "status": "ok",
                "msg": "Login MOCK (Bypass activado)",
                "token": token,
                "user": user_data,
                "origen": "local_bypass"
            }, 200
       

        # Lógica normal para conectar con Docker
        try:
            external_url = f"{Config.PERSON_API_URL}/login"
            payload = {"email": email, "password": password}
            response = requests.post(external_url, json=payload, timeout=2)
            
            if response.status_code == 200:
                user_data = response.json()
                token = self._generate_token(user_data)
                return {"status": "ok", "token": token, "user": user_data}, 200
        except:
            pass 
        
        return {"status": "error", "msg": "No se pudo iniciar sesión"}, 401

    def _generate_token(self, user_data):
        """Genera un token firmado con la clave secreta de Flask"""
        payload = {
            "sub": user_data.get("external_id") or user_data.get("id"),
            "email": user_data.get("email"),
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        return jwt.encode(payload, current_app.config.get("JWT_SECRET_KEY"), algorithm="HS256")
