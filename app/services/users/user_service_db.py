from app.dao.participant_dao import ParticipantDAO
from app.dao.responsible_dao import ResponsibleDAO
from app.schemas.participant_schema import participant_schema, participants_schema


class UserServiceDB:
    def __init__(self):
        self.dao = ParticipantDAO()
        self.responsible_dao = ResponsibleDAO()

    def get_all_users(self):
        result = self.dao.get_all()
        return participants_schema.dump(result)

    def create_user(self, data):
        try:
            nuevo_participante = self.dao.create(
                nombre=data.get('nombre'),
                apellido=data.get('apellido'),
                edad=data.get('edad'),
                dni=data.get('dni'),
                telefono=data.get('telefono'),
                correo=data.get('correo'),
                direccion=data.get('direccion'),
                estado="ACTIVO",
                tipo=data.get('tipo', 'EXTERNO')
            )
            return {
                "status": "ok",
                "msg": "Participante registrado exitosamente",
                "data": participant_schema.dump(nuevo_participante)
            }, 201
        except Exception as e:
            return {
                "status": "error",
                "msg": f"Error al registrar: {str(e)}"
            }, 400

    def create_initiation_participant(self, data):
        """Crea un participante de iniciación con su responsable"""
        try:
            # Separamos los datos del JSON
            datos_nino = data.get('participante')
            datos_padre = data.get('responsable')

            if not datos_nino or not datos_padre:
                return {"status": "error", "msg": "Faltan datos del niño o responsable"}, 400

            # A. Crear al Niño (Participante)
            nuevo_nino = self.dao.create(
                nombre=datos_nino.get('nombre'),
                apellido=datos_nino.get('apellido'),
                edad=datos_nino.get('edad'),
                dni=datos_nino.get('dni'),
                telefono=datos_nino.get('telefono', ''),
                correo=datos_nino.get('correo', ''),
                direccion=datos_nino.get('direccion', ''),
                estado="ACTIVO",
                tipo="INICIACION"
            )

            # B. Crear al Responsable vinculado
            self.responsible_dao.create(
                participant_id=nuevo_nino.id,
                nombre=datos_padre.get('nombre'),
                apellido=datos_padre.get('apellido'),
                dni=datos_padre.get('dni'),
                telefono=datos_padre.get('telefono'),
                parentesco=datos_padre.get('parentesco', 'Representante')
            )

            return {
                "status": "ok",
                "msg": "Niño y representante registrados correctamente",
                "data": {"id_participante": nuevo_nino.id}
            }, 201

        except Exception as e:
            return {"status": "error", "msg": f"Error en registro: {str(e)}"}, 400

    def change_status(self, external_id, nuevo_estado):
        """RF010: Cambiar estado (Activar/Inactivar) - Usa external_id"""
        try:
            # Validar que el estado sea válido
            if nuevo_estado not in ["ACTIVO", "INACTIVO"]:
                return {"status": "error", "msg": "Estado inválido. Use ACTIVO o INACTIVO"}, 400

            # 1. Buscar por external_id
            usuario = self.dao.get_by_external_id(external_id)
            
            if not usuario:
                return {"status": "error", "msg": "Usuario no encontrado"}, 404

            # 2. Actualizar usando el ID interno
            usuario_actualizado = self.dao.update(usuario.id, status=nuevo_estado)

            return {
                "status": "ok",
                "msg": f"Estado actualizado a {nuevo_estado}",
                "data": participant_schema.dump(usuario_actualizado)
            }, 200
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 500

    def search_by_dni(self, dni):
        """RF011: Buscar por DNI"""
        try:
            usuario = self.dao.get_by_dni(dni)
            
            if not usuario:
                return {"status": "error", "msg": "Participante no encontrado"}, 404
                
            return {
                "status": "ok",
                "data": participant_schema.dump(usuario)
            }, 200
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 500
