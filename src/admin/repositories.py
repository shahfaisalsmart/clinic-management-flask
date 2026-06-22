from src.admin.models import Department
from src.auth.models import User, Role
from src.common.database import db

class DepartmentRepository:
    def get_by_name(self, name):
        return Department.query.filter_by(name=name).first()

    def get_by_id(self, department_id):
        return Department.query.get(department_id)

    def get_all(self):
        return Department.query.all()

    def create(self, name, description):
        new_dept = Department(name=name, description=description)
        db.session.add(new_dept)
        db.session.commit()
        return new_dept


class RoleRepository:
    def get_by_name(self, name):
        return Role.query.filter_by(name=name).first()


class UserRepository:
    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def create_user(self, name, email, role_id, password):
        new_user = User(name=name, email=email, role_id=role_id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # ID जनरेट करने के लिए फ्लश किया
        return new_user


