from .roles import RoleList

class Player:
    def __init__(self, user_id):
        self.user_id = user_id
        self.teamleader = False
        self.role = RoleList.RESISTANT
        self.vote_mission = False