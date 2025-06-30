def get_nb_player_on_mission(nb_player: int, round: int):
    if nb_player == 5:
        if round == 1 or round == 3:
            return 2
        else:
            return 3
    if nb_player == 6:
        if round == 1:
            return 2
        elif round == 2 or round == 4:
            return 3
        else:
            return 4
    if nb_player == 7:
        if round == 1:
            return 2
        elif round == 2 or round == 3:
            return 3
        else:
            return 4
    if nb_player == 8:
        if round == 1:
            return 3
        elif round == 2 or round == 3:
            return 4
        else:
            return 5
    if nb_player == 9:
        if round == 1:
            return 3
        elif round == 2 or round == 3:
            return 4
        else:
            return 5
    if nb_player == 10:
        if round == 1:
            return 3
        elif round == 2 or round == 3:
            return 4
        else:
            return 5
    return -1

def need_two_fails(nb_player: int, round: int):
    if nb_player == 5 or nb_player == 6:
        return False
    if round == 4:
        return True
    return False

def get_team_leader_index(players_list: list, current_leader: int):
    index = current_leader + 1
    if index >= len(players_list):
        index = 0
    return index


def get_mission_ctx(nb_player: int, round: int, players_list: list, current_leader: int):
    nb_player_on_mission = get_nb_player_on_mission(nb_player, round)
    need_two_fails_on_mission = need_two_fails(nb_player, round)
    new_leader_index = get_team_leader_index(players_list, current_leader)
    return [nb_player_on_mission, need_two_fails_on_mission, new_leader_index]
