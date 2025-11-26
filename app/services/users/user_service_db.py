from app.models.user import User
# from app.database.db import db

class UserServiceDB:

    def get_all_users(self):
        users = User.query.all()
        return [u.to_dict() for u in users]
