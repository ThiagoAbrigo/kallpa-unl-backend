from app.services import user_service


class UserController:

    def get_users(self):
        return user_service.get_all_users()

    def create_user(self, data):
        return user_service.create_user(data)

    def create_initiation(self, data):
        return user_service.create_initiation_participant(data)
