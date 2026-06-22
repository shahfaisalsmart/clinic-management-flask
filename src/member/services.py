from src.member.repositories import MemberRepository

class MemberService:
    
    def __init__(self):
        self.member_repo = MemberRepository()

    def get_profile(self, user_id):
        member = self.member_repo.get_member_profile(user_id)
        if not member:
            return {"error": "Member not found"}, 404
            
        return {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "role": member.role.name,
            "joined_at": member.created_at.strftime("%Y-%m-%d")
        }, 200

    def update_profile(self, user_id, data):
        if 'name' not in data:
            return {"error": "Name is required to update"}, 400
            
        updated_member = self.member_repo.update_member_name(user_id, data['name'])
        if not updated_member:
            return {"error": "Update failed"}, 400
            
        return {"message": "Member profile updated successfully"}, 200
