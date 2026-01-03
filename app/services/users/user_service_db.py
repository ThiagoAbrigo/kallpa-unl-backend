import uuid
from flask import request
from app.utils.responses import success_response, error_response
from app.models.participant import Participant
from app.models.responsible import Responsible
from app.models.user import User
from app.services.java_sync_service import java_sync
from werkzeug.security import generate_password_hash
from app import db


class UserServiceDB:
    """Servicio de usuarios con PostgreSQL y sincronización con Java."""

    def _get_token(self):
        """Obtiene el token del header Authorization."""
        auth_header = request.headers.get("Authorization", "")
        return auth_header

    def get_all_users(self):
        try:
            participants = Participant.query.all()

            data = [
                {
                    "external_id": p.external_id,
                    "firstName": p.firstName,
                    "lastName": p.lastName,
                    "email": p.email,
                    "dni": p.dni,
                    "age": p.age,
                    "status": p.status,
                    "type": p.type,
                    "java_external": p.java_external,
                }
                for p in participants
            ]

            return success_response(msg="Usuarios listados correctamente", data=data)
        except Exception:
            return error_response("Error interno del servidor", code=500)

    def create_user(self, data):
        """Crea usuario en PostgreSQL y lo sincroniza con el microservicio Java."""
        token = self._get_token()

        try:
            dni = data.get("dni")
            if dni and token:
                java_search = java_sync.search_by_identification(dni, token)
                if java_search.get("found"):
                    return error_response(
                        msg="Usuario ya existe en el sistema central", code=400
                    )

            participant = Participant(
                firstName=data.get("firstName"),
                lastName=data.get("lastName"),
                age=data.get("age"),
                dni=data.get("dni"),
                phone=data.get("phone"),
                email=data.get("email"),
                address=data.get("address"),
                status="ACTIVO",
                type=data.get("type", "EXTERNO"),
            )

            java_synced = False
            java_external = None
            if token:
                if not data.get("email") or not data.get("password"):
                    data["email"] = f"{data.get('dni')}@kallpa.system"
                    data["password"] = str(uuid.uuid4())[:8]

                java_result = java_sync.create_person_with_account(data, token)

                if java_result and java_result.get("success"):
                    java_synced = True
                    java_external = java_result.get("data", {}).get("external")
                    participant.java_external = java_external
                else:
                    print(
                        f"[UserServiceDB] No se pudo sincronizar con Java: {java_result}"
                    )

            db.session.add(participant)
            db.session.commit()

            return success_response(
                msg="Participant successfully registered"
                + (" y sincronizado con Java" if java_synced else ""),
                data={
                    "external_id": participant.external_id,
                    "firstName": participant.firstName,
                    "lastName": participant.lastName,
                    "java_synced": java_synced,
                    "java_external": java_external,
                },
            )
        except Exception as e:
            db.session.rollback()
            return error_response(
                msg=f"Error interno del servidor al registrar el usuario: {str(e)}",
                code=500,
            )

    def create_initiation_participant(self, data):
        """Crea un participante de iniciación con su responsable y sincroniza con Java."""
        token = self._get_token()

        try:
            datos_nino = data.get("participant")
            datos_responsable = data.get("responsible")

            if not datos_nino or not datos_responsable:
                return error_response(
                    msg="Faltan datos del participante o del responsable",
                )

            # Buscar primero en Java si ya existe
            dni = datos_nino.get("dni")
            if dni and token:
                java_search = java_sync.search_by_identification(dni, token)
                if java_search.get("found"):
                    return error_response(
                        msg="Participante ya existe en el sistema central", code=400
                    )

            email = datos_nino.get("email")
            if email == "":
                email = None

            participant = Participant(
                firstName=datos_nino.get("firstName"),
                lastName=datos_nino.get("lastName"),
                age=datos_nino.get("age"),
                dni=datos_nino.get("dni"),
                phone=datos_nino.get("phone"),
                email=email,
                address=datos_nino.get("address"),
                status="ACTIVO",
                type="INICIACION",
            )

            # Sincronizar con Java
            java_synced = False
            if token:
                java_data = {
                    "firstName": datos_nino.get("firstName"),
                    "lastName": datos_nino.get("lastName"),
                    "dni": datos_nino.get("dni"),
                    "phone": datos_nino.get("phone", ""),
                    "address": datos_nino.get("address", ""),
                    "type": "INICIACION",
                    "email": f"{datos_nino.get('dni')}@iniciacion.system",
                    "password": str(uuid.uuid4())[:8],
                }
                java_result = java_sync.create_person_with_account(java_data, token)
                if java_result and java_result.get("success"):
                    java_synced = True
                    participant.java_external = java_result.get("data", {}).get(
                        "external"
                    )

            db.session.add(participant)
            db.session.flush()

            responsible = Responsible(
                name=datos_responsable.get("name"),
                dni=datos_responsable.get("dni"),
                phone=datos_responsable.get("phone"),
                participant_id=participant.id,
            )

            db.session.add(responsible)

            db.session.commit()

            return success_response(
                msg="Participante de iniciación y responsable registrados correctamente"
                + (" y sincronizado con Java" if java_synced else ""),
                data={
                    "participant_external_id": participant.external_id,
                    "responsible_external_id": responsible.external_id,
                    "java_synced": java_synced,
                },
            )

        except Exception as e:
            db.session.rollback()
            return error_response(msg=str(e), code=500)

    def change_status(self, external_id, new_state):
        """RF010: Cambiar estado (Activar/Inactivar) y sincroniza con Java."""
        token = self._get_token()

        try:
            # Validar que el estado sea válido
            if new_state not in ["ACTIVO", "INACTIVO"]:
                return error_response(
                    msg="Estado inválido. Use ACTIVO o INACTIVO",
                )

            participant = Participant.query.filter_by(external_id=external_id).first()

            if not participant:
                return error_response(
                    msg="Participant not found",
                )

            participant.status = new_state
            db.session.commit()

            java_external = participant.java_external
            if token and java_external:
                java_result = java_sync.change_state(java_external, token)
                if java_result and java_result.get("success"):
                    print(
                        f"[UserServiceDB] Estado sincronizado con Java para {java_external}"
                    )
                else:
                    print(
                        f"[UserServiceDB] No se pudo sincronizar estado con Java: {java_result}"
                    )

            return success_response(
                msg=f"Status updated to {new_state}",
                data={"external_id": participant.external_id},
            )

        except Exception:
            db.session.rollback()
            return error_response(
                msg="Error interno del servidor al cambiar el estado", code=500
            )

    def search_by_dni(self, dni):
        """RF011: Buscar por DNI, primero en Java y luego local."""
        token = self._get_token()

        try:
            if token:
                java_result = java_sync.search_by_identification(dni, token)
                if java_result.get("found"):
                    return success_response(
                        msg="Participant found (Java)",
                        data=java_result.get("data"),
                    )

            participant = Participant.query.filter_by(dni=dni).first()

            if not participant:
                return error_response(
                    msg="Participant not found",
                )

            return success_response(
                msg="Participant found",
                data={
                    "external_id": participant.external_id,
                    "firstName": participant.firstName,
                    "lastName": participant.lastName,
                    "dni": participant.dni,
                },
            )
        except Exception:
            db.session.rollback()
            return error_response(
                msg="Error interno del servidor al buscar el participante", code=500
            )

    def search_in_java(self, dni):
        """Busca exclusivamente en el microservicio Java."""
        token = self._get_token()

        if not token:
            return error_response(msg="Token requerido para buscar en Java", code=401)

        java_result = java_sync.search_by_identification(dni, token)
        if java_result.get("found"):
            return success_response(
                msg="Participante encontrado en Java", data=java_result.get("data")
            )

        return error_response(msg="Participante no encontrado en Java", code=404)

    # Revisar Josep
    def create_participant(self, data):
        token = self._get_token()

        try:
            is_minor = data.get("type") == "INICIACION" or data.get("age", 0) < 18

            participant_data = data.get("participant") if is_minor else data
            responsible_data = data.get("responsible") if is_minor else None

            # 1. Validaciones
            self._validate_participant(participant_data, responsible_data, is_minor)

            # 2. Verificar en Java
            self._check_java_duplicate(participant_data, token)

            # 3. Crear participante
            participant = self._build_participant(participant_data, is_minor)
            db.session.add(participant)

            # # 4. Sincronizar Java
            # self._sync_with_java(participant, participant_data, token, is_minor)

            # db.session.add(participant)
            # db.session.flush()

            # 5. Responsable (solo iniciación)
            responsible = None
            if is_minor:
                responsible = self._create_responsible(responsible_data, participant)

            db.session.commit()
            try:
                self._sync_with_java(participant, participant_data, token, is_minor)
            except Exception as e:
                print(f"[Warning] Error sincronizando con Java: {e}")

            return success_response(
                msg="Participante registrado correctamente",
                data={
                    "participant_external_id": participant.external_id,
                    "responsible_external_id": (
                        responsible.external_id if responsible else None
                    ),
                },
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    def _validate_participant(self, participant, responsible, is_minor):
        if not participant:
            raise Exception("Datos del participante incompletos")

        if is_minor and not responsible:
            raise Exception("Se requieren datos del responsable")

    def _build_participant(self, data, is_minor):
        return Participant(
            firstName=data.get("firstName"),
            lastName=data.get("lastName"),
            age=data.get("age"),
            dni=data.get("dni"),
            phone=data.get("phone"),
            email=data.get("email") or None,
            address=data.get("address"),
            status="ACTIVO",
            type="INICIACION" if is_minor else data.get("type", "EXTERNO"),
        )

    def _create_responsible(self, data, participant):
        responsible = Responsible(
            name=data.get("name"),
            dni=data.get("dni"),
            phone=data.get("phone"),
            participant_id=participant.id,
        )
        db.session.add(responsible)
        return responsible

    def _check_java_duplicate(self, participant_data, token):
        if not token:
            return

        dni = participant_data.get("dni")
        if not dni:
            return

        java_search = java_sync.search_by_identification(dni, token)
        if java_search.get("found"):
            raise Exception("Participante ya existe en el sistema central")

    def _sync_with_java(self, participant, participant_data, token, is_minor):
        if not token:
            return

        email = participant_data.get("email")
        password = participant_data.get("password")

        if not email:
            email = f"{participant_data.get('dni')}@kallpa.system"

        if not password:
            password = str(uuid.uuid4())[:8]

        java_data = {
            "firstName": participant_data.get("firstName"),
            "lastName": participant_data.get("lastName"),
            "dni": participant_data.get("dni"),
            "phone": participant_data.get("phone", ""),
            "address": participant_data.get("address", ""),
            "type": (
                "INICIACION" if is_minor else participant_data.get("type", "EXTERNO")
            ),
            "email": email,
            "password": password,
        }

        java_result = java_sync.create_person_with_account(java_data, token)

        if java_result and java_result.get("success"):
            participant.java_external = java_result.get("data", {}).get("external")

    def create_user(self, data):
        try:
            # ---------- Validación general ----------
            if not data or not isinstance(data, dict):
                return {"status": "error", "msg": "Datos inválidos", "code": 400}

            # ---------- Campos obligatorios ----------
            required_fields = [
                "firstName",
                "lastName",
                "dni",
                "email",
                "password",
                "role",
            ]

            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return {
                        "status": "error",
                        "msg": f"El campo '{field}' es obligatorio",
                        "code": 400,
                    }

            # ---------- Validar rol ----------
            allowed_roles = ["DOCENTE", "PASANTE"]
            if data["role"] not in allowed_roles:
                return {"status": "error", "msg": "Rol inválido", "code": 400}

            # ---------- Validar duplicados ----------
            if User.query.filter_by(dni=data["dni"]).first():
                return {
                    "status": "error",
                    "msg": "El DNI ya está registrado",
                    "code": 400,
                }

            if User.query.filter_by(email=data["email"].lower()).first():
                return {
                    "status": "error",
                    "msg": "El correo ya está registrado",
                    "code": 400,
                }

            # ---------- Hashear contraseña ----------
            hashed_password = generate_password_hash(
                data["password"], method="pbkdf2:sha256", salt_length=16
            )

            # ---------- Crear usuario ----------
            user = User(
                firstName=data["firstName"].strip(),
                lastName=data["lastName"].strip(),
                dni=data["dni"].strip(),
                phone=data.get("phone"),
                email=data["email"].lower().strip(),
                password=hashed_password,
                role=data["role"],
                status="ACTIVO",
            )
            db.session.add(user)
            db.session.commit()

            return {
                "status": "success",
                "msg": "Usuario registrado correctamente",
                "code": 200,
                "data": {"external_id": user.external_id, "role": user.role},
            }

        except Exception as e:
            db.session.rollback()
            return {"status": "error", "msg": f"Error interno: {str(e)}", "code": 500}
