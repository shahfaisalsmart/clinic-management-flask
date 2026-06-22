from src.common.database import db
from src.auth.models import User

class MemberRepository:
    
    def get_member_profile(self, user_id):
        return User.query.filter_by(id=user_id).first()

    def update_member_name(self, user_id, new_name):
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.name = new_name
            db.session.commit()
            return user
        return None
