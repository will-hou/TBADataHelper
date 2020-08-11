from tbapy import TBA


# Given a match and a team, return which alliance a team was on
def get_alliance_color(match, team_key):
    if team_key in match["alliances"]["blue"]["team_keys"]:
        return "blue"
    elif team_key in match["alliances"]["red"]["team_keys"]:
        return "red"
    else:
        return None


# Given a match and a team, return which number the robot was classified under in TBA
def get_robot_number(match, team_key):
    return match["alliances"][get_alliance_color(match, team_key)]["team_keys"].index(
        team_key) + 1


# Return whether a match existed
def check_match_exists(match):
    if match['score_breakdown'] is None:
        print("Found a nonexistent match")
        return False
    else:
        return True


# Return True if matches exist for a certain event or team
def check_matches_exist(authkey, year, team_key=None, event_key=None, exclude_playoffs=False):
    tba = TBA(authkey)
    if event_key is not None and team_key is None:
        if exclude_playoffs and len(get_qualification_matches(tba.event_matches(event=event_key))) == 0:
            return False
        elif not exclude_playoffs and len(tba.event_matches(event=event_key)) == 0:
            return False
        else:
            return True
    if team_key is not None and event_key is None:
        if exclude_playoffs and len(get_qualification_matches(tba.team_matches(team=team_key, year=year))) == 0:
            return False
        elif len(tba.team_matches(team=team_key, year=year)) == 0:
            return False
        else:
            return True
    elif team_key is not None and event_key is not None:
        print('Make sure to only specify team_key OR event_key, not both')
        return None


# Given a list of matches, returns the list with non qualification matches removed
def get_qualification_matches(matches):
    quals = []
    for match in matches:
        if match["comp_level"] == "qm":
            quals.append(match)
    return quals


# Given a list of matches, returns the list with matches that haven't been played removed
def get_played_matches(matches):
    played = []
    for match in matches:
        if match["score_breakdown"] is not None:
            played.append(match)
    return played
