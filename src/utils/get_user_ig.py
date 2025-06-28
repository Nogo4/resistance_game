from main import Game
from game import Player, current_games, current_players

def get_user_ig(user_id: int):
    if user_id not in current_players:
        return None
    for game in current_games:
        for player in game.players:
            if player.user_id == user_id:
                return player
    return None
