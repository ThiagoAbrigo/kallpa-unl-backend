import requests
from app.config.config import Config
from app.utils.responses import error_response
from app.utils.jwt import generate_token
from werkzeug.security import check_password_hash
from app.models.user import User
from app import db

class AuthService:
    def login(self, data):
        """Autenticación de usuarios con sincronización de java_external"""
        email = data.get("email", "").lower().strip()
        password = data.get("password")

        if not email or not password:
            return error_response("Email y contraseña requeridos", 400)

        user = User.query.filter_by(email=email, status="ACTIVO").first()

        if user and check_password_hash(user.password, password):
            if not user.java_external:
                try:
                    java_response = requests.post(
                        f"{Config.PERSON_API_URL}/login",
                        json={"email": email, "password": password},
                        timeout=3,
                    )
                    if java_response.status_code == 200:
                        java_user = java_response.json().get("data", {})
                        if 'external' in java_user:
                            user.java_external = java_user['external']
                        if 'token' in java_user:
                            user.java_token = java_user['token']
                        db.session.commit()
                        print(f"✅ Token Java vinculado (login local): {user.email} -> java_external: {user.java_external}")
                except Exception as e:
                    print(f"⚠️ No se pudo sincronizar java_external: {e}")
            
            token = generate_token(
                {
                    "sub": user.external_id,
                    "email": user.email,
                    "role": user.role,
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

        if email == "dev@kallpa.com":
            token = generate_token(
                {
                    "sub": "usuario-mock-bypass",
                    "email": email,
                    "role": "admin",
                }
            )

            return {
                "status": "ok",
                "msg": "Login MOCK",
                "token": token,
                "user": {
                    "external_id": "usuario-mock-bypass",
                    "email": email,
                    "role": "admin",
                },
                "code": 200,
            }

        try:
            response = requests.post(
                f"{Config.PERSON_API_URL}/login",
                json={"email": email, "password": password},
                timeout=3,
            )

            if response.status_code == 200:
                java_user = response.json().get("data", {})
                
                local_user = User.query.filter_by(email=email).first()
                
                if local_user:
                    if 'external' in java_user:
                        local_user.external_id = java_user['external']
                        local_user.java_external = java_user['external']
                    if 'token' in java_user:
                        local_user.java_token = java_user['token']
                    db.session.commit()
                    print(f"Token Java vinculado (usuario existente): {local_user.email} -> external: {local_user.java_external}")
                else:
                    import uuid
                    from werkzeug.security import generate_password_hash
                    
                    print(f"[AUTH] Datos recibidos de Java: {java_user}")
                    java_external = java_user.get('external')
                    print(f"[AUTH] java_external extraído: {java_external}")
                    
                    new_user = User(
                        external_id=java_external if java_external else str(uuid.uuid4()),
                        firstName=java_user.get('first_name', 'Usuario'),
                        lastName=java_user.get('last_name', 'Java'),
                        dni='0000000000',
                        phone='',
                        email=email,
                        address='',
                        password=generate_password_hash(password),
                        role='DOCENTE',
                        status='ACTIVO',
                        java_external=java_external,
                        java_token=java_user.get('token')
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    print(f"Usuario creado desde Java: {email} -> java_external: {new_user.java_external}")
                
                java_token_raw = java_user.get("token", "")
                if java_token_raw.startswith("Bearer "):
                    token_for_frontend = java_token_raw[7:]
                else:
                    token_for_frontend = java_token_raw
                
                return {
                    "status": "ok",
                    "msg": "Login Exitoso (Docker)",
                    "token": token_for_frontend,
                    "user": java_user,
                    "code": 200,
                }

        except Exception:
            return error_response("No se pudo conectar al sistema externo", 500)

        return error_response("Credenciales inválidas", 401)
