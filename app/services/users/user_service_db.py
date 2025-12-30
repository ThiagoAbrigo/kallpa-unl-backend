from flask import request
from app.utils.responses import success_response, error_response
from app.models.participant import Participant
from app.models.responsible import Responsible
from app.services.java_sync_service import java_sync
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
                        msg="Usuario ya existe en el sistema central",
                        code=400
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
                if data.get("email") and data.get("password"):
                    java_result = java_sync.create_person_with_account(data, token)
                else:
                    java_result = java_sync.create_person(data, token)

                if java_result and java_result.get("success"):
                    java_synced = True
                    java_external = java_result.get("data", {}).get("external")
                    participant.java_external = java_external
                else:
                    print(f"[UserServiceDB] No se pudo sincronizar con Java: {java_result}")

            db.session.add(participant)
            db.session.commit()

            return success_response(
                msg="Participant successfully registered" + (" y sincronizado con Java" if java_synced else ""),
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
                msg=f"Error interno del servidor al registrar el usuario: {str(e)}", code=500
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
                        msg="Participante ya existe en el sistema central",
                        code=400
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
                }
                java_result = java_sync.create_person(java_data, token)
                if java_result and java_result.get("success"):
                    java_synced = True
                    participant.java_external = java_result.get("data", {}).get("external")

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
                msg="Participante de iniciación y responsable registrados correctamente" + (" y sincronizado con Java" if java_synced else ""),
                data={
                    "participant_external_id": participant.external_id,
                    "responsible_external_id": responsible.external_id,
                    "java_synced": java_synced,
                },
            )

        except Exception as e:
            db.session.rollback()
            return error_response(
                msg=str(e),
                code=500
            )


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
                    print(f"[UserServiceDB] Estado sincronizado con Java para {java_external}")
                else:
                    print(f"[UserServiceDB] No se pudo sincronizar estado con Java: {java_result}")

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
                msg="Participante encontrado en Java",
                data=java_result.get("data")
            )

        return error_response(msg="Participante no encontrado en Java", code=404)
