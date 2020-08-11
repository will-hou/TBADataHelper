import numpy as np
from .utils import *
from tbapy import TBA

# Log full length arrays in the console
np.set_printoptions(threshold=np.inf)

"""
This class calculates the contributed contribution (CC) of all the teams at an event for one given metric.

Parameters:
--------------------------------------------------------------
event_key: string = the TBA key of an event.
metric: string = the TBA/FIRSTApi metric to calculate contribution for.
exclude_playoffs: boolean = whether to include playoff matches in CC calculations. Default = True

Returns:
calculated_contribution: dictionary {team_key: CC, ...} = A dictionary with keys being TBA team_keys and values being the team's CC at the event
---------------------------------------------------------------
"""


class event_OPR:
    def __init__(self, authkey, event_key, metric, exclude_playoffs=True):
        # TBA data handler
        self.tba = TBA(authkey)

        self.matches = get_qualification_matches(
            self.tba.event_matches(event=event_key)) if exclude_playoffs else self.tba.event_matches(event=event_key)

        # Only keep matches that have been played
        self.matches = get_played_matches(self.matches)

        # Which event to calculate contributions for
        self.event_key = event_key
        # Which metric to calculate contribution by
        self.metric = metric

        self.team_matrix_map = self.create_team_matrix_map()
        self.alliances_matrix = self.create_alliances_matrix()
        self.scores_matrix = self.create_score_matrix()

    # This function associates each team with a particular column in the alliances matrix
    def create_team_matrix_map(self):
        team_matrix_position = 0
        # Keys are the team-key. Value is the team's column index in the matrix
        team_matrix_map = {}
        for match in self.matches:
            for alliance_color in ['blue', 'red']:
                for team in match['alliances'][alliance_color]['team_keys']:
                    if team not in team_matrix_map:
                        team_matrix_map[team] = team_matrix_position
                        team_matrix_position += 1
        return team_matrix_map

    # Initializes a matrix with the total number of matches (multiplied by 2 to account for the two alliances per match)as rows
    # and the total number of teams present at the event as columns
    def create_alliances_matrix(self):
        alliances_matrix = np.zeros((len(self.matches) * 2, max(self.team_matrix_map.values()) + 1))
        # Counter to keep track of the row each match corresponds to in the matrix
        match_position = 0
        for match in self.matches:
            # Replaces 0 with 1 in the team's position in the matrix if they played during that match
            for alliance_color in ['blue', 'red']:
                for team in match['alliances'][alliance_color]['team_keys']:
                    alliances_matrix[match_position, self.team_matrix_map[team]] = 1
                match_position += 1
        return alliances_matrix

    # This function creates a 1 column matrix with each row containing the value of the given metric for a particular alliance in a match
    def create_score_matrix(self):
        # Creates a matrix equal to the length of all the matches (multiplied by 2 to account for the two alliances)
        scores_matrix = np.vstack(np.zeros(len(self.matches) * 2))
        match_position = 0
        for match in self.matches:
            for alliance_color in ['blue', 'red']:
                scores_matrix[match_position] = match['score_breakdown'][alliance_color][self.metric]
                match_position += 1
        return scores_matrix

    # This function solves the matrix and returns a dictionary of team_keys and their CCs
    def calculate_contribution(self):
        solutions, residuals, _, _ = np.linalg.lstsq(self.alliances_matrix, self.scores_matrix, rcond=None)
        # Return the calculated contribution for for the given

        calculated_contributions = {}
        counter = 0
        # Creates a dictionary with keys being TBA team keys and values being that team's CC for the given metric
        for (index, team) in enumerate(self.team_matrix_map):
            calculated_contributions[team] = solutions[index][0]
            counter += 1

        return calculated_contributions


"""
THE FOLLOWING IS NOT THE CORRECT APPROACH TO CALCULATING OPR. IT IS NOT USED.
This class calculates the contributed contribution (CC) of a team out of all of their played matches for one given metric.

Parameters:
--------------------------------------------------------------
team_key: string = the TBA key of a team.
year: int = the year that matches belong too.
metric: string = the TBA/FIRSTApi metric to calculate contribution for.
exclude_playoffs: boolean = whether to include playoff matches in CC calculations. Default = True

Returns:
calculated_contribution: float = The calculated contribution of a team to a particular metric.
---------------------------------------------------------------
"""


class team_OPR:
    def __init__(self, authkey, team_key, year, metric, exclude_playoffs=True):
        # TBA data handler
        self.tba = TBA(authkey)
        # Which team to calculate contribution for
        self.team_key = team_key
        # The metric to calculate contribution by
        self.metric = metric

        self.matches = get_qualification_matches(
            self.tba.team_matches(team=self.team_key, year=year)) if exclude_playoffs else self.tba.team_matches(
            team=self.team_key, year=year)

        # Only keep matches that have been played
        self.matches = get_played_matches(self.matches)

        self.team_matrix_map = self.create_team_matrix_map()
        self.alliances_matrix = self.create_alliances_matrix()
        self.scores_matrix = self.create_scores_matrix()

    # This function associates each team with a particular column in the alliances matrix
    def create_team_matrix_map(self):
        team_matrix_position = 0
        # Keys are the team-key. Values are the column a team is located under in the matrix
        team_matrix_map = {}
        for match in self.matches:
            # Loop through all the teams in a match
            for team in match['alliances'][get_alliance_color(match, self.team_key)]['team_keys']:
                if team not in team_matrix_map:
                    team_matrix_map[team] = team_matrix_position
                    team_matrix_position += 1
        return team_matrix_map

    # Initializes a matrix with the total number of matches as rows and the total number of teams the team has ever played with as columns
    def create_alliances_matrix(self):
        # Initializes a matrix with the total number of matches as rows and the total number of teams present as columns
        alliances_matrix = np.zeros((len(self.matches), max(self.team_matrix_map.values()) + 1))
        # Counter to keep track of the row each match corresponds to in the matrix
        match_num = 0
        for match in self.matches:
            # Replaces 0 with 1 in the team's position in the matrix if they played during that match
            for team in match['alliances'][get_alliance_color(match, self.team_key)]['team_keys']:
                alliances_matrix[match_num, self.team_matrix_map[team]] = 1
            match_num += 1
        return alliances_matrix

    def create_scores_matrix(self):
        scores_matrix = np.vstack(np.zeros(len(self.matches)))
        match_num = 0
        for match in self.matches:
            scores_matrix[match_num] = match['score_breakdown'][get_alliance_color(match, self.team_key)][self.metric]
            match_num += 1
        return scores_matrix

    def calculate_contribution(self):
        # Solve the system of equations
        solutions, residuals, _, _ = np.linalg.lstsq(self.alliances_matrix, self.scores_matrix, rcond=None)
        # Return the calculated contribution for for the given team
        return solutions[self.team_matrix_map[self.team_key]][0]
