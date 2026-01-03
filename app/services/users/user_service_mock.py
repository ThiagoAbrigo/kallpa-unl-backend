import json
import os
import uuid
from flask import request
from app.utils.responses import success_response, error_response
from app.services.java_sync_service import java_sync


class UserServiceMock:
    """Servicio de usuarios con almacenamiento mock (JSON) y sincronización con Java."""

    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        print("BASE:", base)
        self.mock_path = os.path.join(base, "mock", "users.json")
        print("MOCK PATH:", self.mock_path)

    def _get_token(self):
        """Obtiene el token del header Authorization."""
        auth_header = request.headers.get("Authorization", "")
        return auth_header

    def _load(self):
        with open(self.mock_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.mock_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all_users(self):
        users = self._load()
        return success_response(
            msg="Usuarios obtenidos correctamente (MOCK)",
            data=users
        )

    def get_participants_only(self):
        """Obtiene solo los participantes (excluye docentes, administrativos, pasantes)."""
        users = self._load()
        # Tipos que NO son participantes (son staff/profesores)
        staff_types = ["DOCENTE", "ADMINISTRATIVO", "PASANTE", "PROFESOR", "ADMIN"]
        
        # Filtrar solo participantes activos
        participants = [
            u for u in users 
            if u.get("type", "").upper() not in staff_types 
            and u.get("status", "").upper() == "ACTIVO"
        ]
        
        return success_response(
            msg="Participantes obtenidos correctamente (MOCK)",
            data=participants
        )

    def create_user(self, data):
        """Crea usuario localmente y lo sincroniza con el microservicio Java."""
        token = self._get_token()
        users = self._load()

        dni = data.get("dni")
        if dni and token:
            java_search = java_sync.search_by_identification(dni, token)
            if java_search.get("found"):
                return error_response(
                    msg="Usuario ya existe en el sistema central",
                    code=400
                )

        new_id = max([u.get("id", 0) for u in users], default=0) + 1

        new_user = {
            "id": new_id,
            "firstName": data.get("firstName"),
            "lastName": data.get("lastName"),
            "age": data.get("age"),
            "dni": data.get("dni"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "address": data.get("address"),
            "status": "ACTIVO",
            "type": data.get("type", "ESTUDIANTE"),
        }

        java_result = None
        if token:
            if not data.get("email") or not data.get("password"):
                data["email"] = f"{data.get('dni')}@kallpa.system"
                data["password"] = str(uuid.uuid4())[:8]

            java_result = java_sync.create_person_with_account(data, token)

            if java_result and java_result.get("success"):
                new_user["java_synced"] = True
                new_user["java_external"] = java_result.get("data", {}).get("external")
            else:
                new_user["java_synced"] = False
                print(f"[UserServiceMock] No se pudo sincronizar con Java: {java_result}")

        users.append(new_user)
        self._save(users)

        return success_response(
            msg="Participante registrado exitosamente (MOCK)" + (" y sincronizado con Java" if new_user.get("java_synced") else ""),
            data=new_user,
            code=201
        )

    def create_initiation_participant(self, data):
        """Crea un participante de iniciación con su responsable y sincroniza con Java."""
        token = self._get_token()
        users = self._load()

        datos_nino = data.get("participant")
        datos_padre = data.get("responsible")

        if not datos_nino or not datos_padre:
            return error_response(
                msg="Faltan datos del niño o responsable",
                code=400
            )

        dni = datos_nino.get("dni")
        if dni and token:
            java_search = java_sync.search_by_identification(dni, token)
            if java_search.get("found"):
                return error_response(
                    msg="Participante ya existe en el sistema central",
                    code=400
                )

        new_id = max([u.get("id", 0) for u in users], default=0) + 1

        new_participant = {
            "id": new_id,
            "firstName": datos_nino.get("firstName"),
            "lastName": datos_nino.get("lastName"),
            "age": datos_nino.get("age"),
            "dni": datos_nino.get("dni"),
            "phone": datos_nino.get("phone", ""),
            "email": datos_nino.get("email", ""),
            "address": datos_nino.get("address", ""),
            "status": "ACTIVO",
            "type": "INICIACION",
            "responsible": {
                "name": datos_padre.get("name"),
                "dni": datos_padre.get("dni"),
                "phone": datos_padre.get("phone"),
                "relationship": datos_padre.get("relationship", "Representante"),
            },
        }

        if token:
            java_data = {
                "firstName": datos_nino.get("firstName"),
                "lastName": datos_nino.get("lastName"),
                "dni": datos_nino.get("dni"),
                "phone": datos_nino.get("phone", ""),
                "address": datos_nino.get("address", ""),
                "type": "INICIACION",
                "email": f"{datos_nino.get('dni')}@iniciacion.system",
                "password": str(uuid.uuid4())[:8]
            }
            java_result = java_sync.create_person_with_account(java_data, token)
            if java_result and java_result.get("success"):
                new_participant["java_synced"] = True
                new_participant["java_external"] = java_result.get("data", {}).get("external")
            else:
                new_participant["java_synced"] = False

        users.append(new_participant)
        self._save(users)

        return success_response(
            msg="Participante de iniciación y responsable registrados correctamente (MOCK)" + (" y sincronizado con Java" if new_participant.get("java_synced") else ""),
            data=new_participant,
            code=201
        )

    def change_status(self, user_id, nuevo_estado):
        """Cambia el estado de un participante y sincroniza con Java."""
        token = self._get_token()
        users = self._load()

        user_found = None
        for user in users:
            if user.get("id") == user_id:
                user_found = user
                break

        if not user_found:
            return error_response(msg="Participante no encontrado", code=404)

        user_found["status"] = nuevo_estado
        self._save(users)

        java_external = user_found.get("java_external")
        if token and java_external:
            java_result = java_sync.change_state(java_external, token)
            if java_result and java_result.get("success"):
                print(f"[UserServiceMock] Estado sincronizado con Java para {java_external}")
            else:
                print(f"[UserServiceMock] No se pudo sincronizar estado con Java: {java_result}")

        return success_response(
            msg=f"Estado actualizado a {nuevo_estado} (MOCK)",
            data=user_found
        )

    def search_by_dni(self, dni):
        """Busca un participante por DNI, primero en Java y luego local."""
        token = self._get_token()

        if token:
            java_result = java_sync.search_by_identification(dni, token)
            if java_result.get("found"):
                return success_response(
                    msg="Participante encontrado (Java)",
                    data=java_result.get("data")
                )

        users = self._load()
        for user in users:
            if user.get("dni") == dni:
                return success_response(
                    msg="Participante encontrado (MOCK)",
                    data=user
                )

        return error_response(msg="Participante no encontrado", code=404)

    def search_in_java(self, dni):
        """Busca exclusivamente en el microservicio Java."""
        token = self._get_token()

        if not token:
            return error_response(msg="Token requerido para buscar en Java", code=401)

        java_result = java_sync.search_by_identification(dni, token)
        if java_result.get("found"):
            return success_response(
                msg="Participante encontrado en Java",
                data=java_result.get("data")
            )

        return error_response(msg="Participante no encontrado en Java", code=404)
