from tbapy import TBA
from .utils import *
from statistics import mean, mode, stdev, median

"""
- This function returns the average value of a given field
- If the field values are categorical, the most frequent value will be returned
- If the field is categorized in TBA based on robot position, the field_position_based and categorical_value 
    parameters need to be specified. The percentage of times that categorical_value was recorded for the team will be returned in 
    decimal form.

Parameters:
team_key:string = the TBA key of a team
year:int = the year the field is from
field_name:string = the TBA field under scoring_breakdown to get averages for
field_position_based: boolean = whether the field is categorized in TBA based on robot_position. default=false
categorical_value:string = the categorical value to get averages by
exclude_playoff: boolean = whether to exclude playoff matches from calculations
event_key: string = if specified, only include matches played at the given event in calculations.
"""


def get_field_statistic(authkey, team_key, year, field_name, calculations=[],
                         field_position_based=False, categorical_value=None, exclude_playoffs=True, event_key=None):
    # TBA data handler
    tba = TBA(authkey)

    # Get list of team matches from TBA
    if event_key:
        matches = tba.team_matches(team=team_key, event=event_key)
    else:
        matches = tba.team_matches(team=team_key, year=year)

    matches = get_qualification_matches(matches) if exclude_playoffs else matches

    # Only keep matches that have been played
    matches = get_played_matches(matches)

    # Handles fields that are measured through a robot's position, ex. endgame location
    if field_position_based:
        if categorical_value is None:
            print("You must specify a categorical_value to count occurrences of. See docstring for more info")
            return
        field_values = []
        for match in matches:
            # Finds the robot's position number in TBA
            robot_position = str(get_robot_number(match, team_key))
            field_values.append(
                match['score_breakdown'][get_alliance_color(match, team_key)][field_name + robot_position])
        return round(field_values.count(categorical_value) / len(field_values), 3) if len(
            field_values) != 0 else None

    # Creates a list of all the values for a particular field in every match a team played
    field_values = [match["score_breakdown"][get_alliance_color(match, team_key)][field_name] for match in matches]

    # Associates a calculation keyword to its appropriate function
    calculation_map = {'mean': mean, 'med': median, 'max': max, 'min': min, 'stdev': stdev, 'count': len}

    # If the field values are integers, return the average value. If they are strings, return the value that occurs most often

    # Dictionary of {calculation keyword:value} pairs to be returned
    calculated_statistics = {}

    # Perform statistical calculations on list of field values
    # print(field_values)
    for calculation in calculations:
        calculated_statistics[calculation] = calculation_map[calculation](field_values)

    return calculated_statistics


"""
OLD: Use get_average_field with field_position_based and categorical_value parameters instead for greater flexibility
"""

# Returns how often a team climbed to a particular HAB level
# def get_average_climb(team_key, year, hablevel=None):
#     matches = get_team_matches(team_key, year)
#     # List of all a robot's ending locations
#     climbs = []
#     for match in matches:
#         if check_match_exists(match):
#             # Finds the robot's number in TBA
#             robot_number = get_robot_number(match, team_key)
#             # Adds all a robot's ending locations to list
#             climbs.append(
#                 match['score_breakdown'][get_alliance_color(match, team_key)]['endgameRobot{}'.format(robot_number)])
#     return round(climbs.count('HabLevel{}'.format(hablevel)) / len(climbs), 3) if len(climbs) != 0 else None
