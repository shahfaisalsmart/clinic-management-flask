from src.auth.models import User, Role
from src.common.database import db

class AuthRepository:
    
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_role_by_name(self, role_name):
        return Role.query.filter_by(name=role_name).first()

    def create_user(self, name, email, role_id, password):
        new_user = User()
        new_user.name = name
        new_user.email = email
        new_user.role_id = role_id
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        return new_user

    """  
    def create_test(self, id, name):
        new_test = Test()
        new_test.id = id
        new_test.name = name
        return new_test.to_dict()
        """
    


