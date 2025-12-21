from app.utils.responses import success_response, error_response
from app.models.participant import Participant
from app.models.responsible import Responsible
from app import db


class UserServiceDB:

    def get_all_users(self):
        try:
            participants = Participant.query.all()

            data = [
                {
                    "external_id": p.external_id,
                    "firstName": p.firstName,
                    "lastName": p.lastName,
                    "email": p.email,
                    "status": p.status,
                    "type": p.type,
                }
                for p in participants
            ]

            return success_response(msg="Usuarios listados correctamente", data=data)
        except Exception:
            return error_response("Error interno del servidor", code=500)

    def create_user(self, data):
        try:
            participant = Participant(
                firstName=data.get("nombre"),
                lastName=data.get("apellido"),
                age=data.get("edad"),
                dni=data.get("dni"),
                phone=data.get("telefono"),
                email=data.get("correo"),
                address=data.get("direccion"),
                status="ACTIVO",
                type=data.get("tipo", "EXTERNO"),
            )
            db.session.add(participant)
            db.session.commit()
            return success_response(
                msg="Participant successfully registered",
                data={
                    "external_id": participant.external_id,
                    "firstName": participant.firstName,
                    "lastName": participant.lastName,
                },
            )
        except Exception:
            db.session.rollback()
            return error_response(
                msg="Error interno del servidor al registrar el usuario", code=500
            )

    def create_initiation_participant(self, data):
        """Crea un participante de iniciación con su responsable"""
        try:
            datos_nino = data.get("participante")
            datos_responsable = data.get("responsable")

            if not datos_nino or not datos_responsable:
                return error_response(
                    msg="Faltan datos del participante o del responsable",
                )

            # 1. Crear participante (niño)
            participant = Participant(
                firstName=datos_nino.get("nombre"),
                lastName=datos_nino.get("apellido"),
                age=datos_nino.get("edad"),
                dni=datos_nino.get("dni"),
                phone=datos_nino.get("telefono"),
                email=datos_nino.get("correo"),
                address=datos_nino.get("direccion"),
                status="ACTIVO",
                type="INICIACION",
            )

            db.session.add(participant)
            db.session.flush()  

            # 2. Crear responsable
            responsible = Responsible(
                name=datos_responsable.get("nombre"),
                dni=datos_responsable.get("dni"),
                phone=datos_responsable.get("telefono"),
                participant_id=participant.id,
            )

            db.session.add(responsible)

            # 3. Confirmar transacción
            db.session.commit()

            return success_response(
                msg="Participante de iniciación y responsable registrados correctamente",
                data={
                    "participant_external_id": participant.external_id,
                    "responsible_external_id": responsible.external_id,
                },
            )

        except Exception:
            db.session.rollback()
            return error_response(
                msg="Error interno del servidor al registrar la iniciación",
                code=500
            )


    def change_status(self, external_id, new_state):
        """RF010: Cambiar estado (Activar/Inactivar) - Usa external_id"""
        try:
            # Validar que el estado sea válido
            if new_state not in ["ACTIVO", "INACTIVO"]:
                return error_response(
                    msg="Estado inválido. Use ACTIVO o INACTIVO",
                )

            # 1. Buscar por external_id
            participant = Participant.query.filter_by(external_id=external_id).first()

            if not participant:
                return error_response(
                    msg="Participant not found",
                )

            # 2. Actualizar usando el ID interno
            participant.status = new_state
            db.session.commit()

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
        """RF011: Buscar por DNI"""
        try:
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
