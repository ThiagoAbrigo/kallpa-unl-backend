import json
import os
from app.utils.responses import success_response, error_response


class UserServiceMock:

    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        print("BASE:", base)
        self.mock_path = os.path.join(base, "mock", "users.json")
        print("MOCK PATH:", self.mock_path)

    def _load(self):
        with open(self.mock_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.mock_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all_users(self):
        return self._load()

    def create_user(self, data):
        users = self._load()

        # Generar nuevo ID
        new_id = max([u.get("id", 0) for u in users], default=0) + 1

        # Crear nuevo usuario
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

        users.append(new_user)
        self._save(users)

        return success_response(
            msg="Participante registrado exitosamente (MOCK)",
            data=new_user,
            code=201
        )

    def create_initiation_participant(self, data):
        """Crea un participante de iniciación con su responsable (versión MOCK)"""
        users = self._load()

        # Separar datos
        datos_nino = data.get("participant")
        datos_padre = data.get("responsible")

        if not datos_nino or not datos_padre:
            return error_response(
                msg="Faltan datos del niño o responsable",
                code=400
            )

        # Generar nuevo ID
        new_id = max([u.get("id", 0) for u in users], default=0) + 1

        # Crear participante de iniciación
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

        users.append(new_participant)
        self._save(users)

        return success_response(
            msg="Participante de iniciación y responsable registrados correctamente (MOCK)",
            data=new_participant,
            code=201
        )

    def change_status(self, user_id, nuevo_estado):
        """Cambia el estado de un participante (versión MOCK)"""
        users = self._load()

        # Buscar el usuario por ID
        user_found = None
        for user in users:
            if user.get("id") == user_id:
                user_found = user
                break

        if not user_found:
            return error_response(msg="Participante no encontrado", code=404)

        # Actualizar el estado
        user_found["status"] = nuevo_estado
        self._save(users)

        return success_response(
            msg=f"Estado actualizado a {nuevo_estado} (MOCK)",
            data=user_found
        )

    def search_by_dni(self, dni):
        """Busca un participante por DNI (versión MOCK)"""
        users = self._load()

        # Buscar el usuario por DNI
        for user in users:
            if user.get("dni") == dni:
                return success_response(
                    msg="Participante encontrado (MOCK)",
                    data=user
                )

        return error_response(msg="Participante no encontrado", code=404)
