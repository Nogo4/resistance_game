from game import Player

class Mission:
    def __init__(self):
        self.players_list = []
        self.result_list = []
    
    def player_in_list(self, player_id: int):
        for p in self.players_list:
            if p.user_id == player_id:
                return True
        return False
    
    def add_vote(self, player, result: str):
        if not self.player_in_list(player.user_id):
            return 84
        player.vote_mission = True
        self.result_list.append(result)
