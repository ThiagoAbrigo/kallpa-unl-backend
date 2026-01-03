from app.services import user_service


class UserController:

    def get_users(self):
        return user_service.get_all_users()

    def get_participants_only(self):
        """Obtiene solo participantes (sin docentes, administrativos, etc.)"""
        return user_service.get_participants_only()

    def create_user(self, data):
        return user_service.create_user(data)

    def create_initiation(self, data):
        return user_service.create_initiation_participant(data)

    def update_status(self, external_id, data):
        nuevo_estado = data.get('estado')
        if not nuevo_estado:
            return {"status": "error", "msg": "Falta el campo 'estado'"}, 400
        return user_service.change_status(external_id, nuevo_estado)

    def search_user(self, dni):
        return user_service.search_by_dni(dni)

    def search_in_java(self, dni):
        """Busca exclusivamente en el microservicio Java."""
        return user_service.search_in_java(dni)

    #Revisar Josep
    def create_participant(self, data):
        """
        Registra un participante (mayor o menor de edad).
        Si es menor, espera datos de responsable.
        """
        return user_service.create_participant(data)

    def create_user(self, data):
        return user_service.create_user(data)
