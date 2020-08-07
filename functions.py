from tbapy import TBA
from .utils import *
from statistics import mean, mode, stdev

"""
- This function returns the average value of a given metric
- If the metric values are categorical, the most frequent value will be returned
- If the metric is categorized in TBA based on robot position, the metric_position_based and categorical_value 
    parameters need to be specified. The percentage of times that categorical_value was recorded for the team will be returned in 
    decimal form.

Parameters:
team_key:string = the TBA key of a team
year:int = the year the metric is from
metric_name:string = the TBA metric under scoring_breakdown to get averages for
metric_position_based: boolean = whether the metric is categorized in TBA based on robot_position. default=false
categorical_value:string = the categorical value to get averages by
"""


def get_metric_statistic(authkey, team_key, year, metric_name, calculations=[], metric_position_based=False,
                         categorical_value=None,
                         exclude_playoffs=False):
    # TBA data handler
    tba = TBA(authkey)

    # Get list of team matches from TBA
    matches = get_qualification_matches(
        tba.team_matches(team=team_key, year=year)) if exclude_playoffs else tba.team_matches(
        team=team_key, year=year)

    # Only keep matches that have been played
    matches = get_played_matches(matches)

    # Handles metrics that are measured through a robot's position, ex. endgame location
    if metric_position_based:
        if categorical_value is None:
            print("You must specify a categorical_value to count occurences of. See docstring for more info")
            return
        metric_values = []
        for match in matches:
            # Finds the robot's position number in TBA
            robot_position = str(get_robot_number(match, team_key))
            metric_values.append(
                match['score_breakdown'][get_alliance_color(match, team_key)][metric_name + robot_position])
        return round(metric_values.count(categorical_value) / len(metric_values), 3) if len(
            metric_values) != 0 else None

    # Creates a list of all the values for a particular metric in every match a team played
    metric_values = [match["score_breakdown"][get_alliance_color(match, team_key)][metric_name] for match in matches]

    # Associates a calculation keyword to its appropriate function
    calculation_map = {'mean': mean, 'max': max, 'min': min, 'stdev': stdev, 'count': len}

    # If the metric values are integers, return the average value. If they are strings, return the value that occurs most often

    # Dictionary of {calculation keyword:value} pairs to be returned
    calculated_statistics = {}

    # Perform statistical calculations on list of metric values
    print(metric_values)
    for calculation in calculations:
        calculated_statistics[calculation] = calculation_map[calculation](metric_values)

    return calculated_statistics


"""
OLD: Use get_average_metric with metric_position_based and categorical_value parameters instead for greater flexibility
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
