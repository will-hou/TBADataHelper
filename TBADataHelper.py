from .functions import *
from .opr import *
from tbapy import TBA
from statistics import stdev


class TBADataHelper:
    """
    Class for performing aggregate and OPR calculations on match data fetched from TBA APIv3

    Constructor arguments:
    year: int = The year to get data from
    """

    def __init__(self, authkey, year, team_key=None, event_key=None):
        self.authkey = authkey
        self.year = year

        # TBA data handler
        self.tba = TBA(authkey)

    def get_team_field_statistics(self, team_key, field_name, calculations=['mean'], field_position_based=False,
                             categorical_value=None, exclude_playoffs=True, event_key=None):
        """
        Returns a dictionary of calculated statistics mean/med/min/max/stdev/count for a given field (ex. totalPoints)

        - If the field is categorized in TBA based on robot position(ex. endgameRobot2, etc.), the field_position_based
        and categorical_value parameters need to be specified. The percentage of times that categorical_value was recorded
        for the team will be returned in decimal form.

        Required Parameters:
        team_key: str = the team key ('frc'+ TEAM_NUMBER) to get calculations for
        field_name: str = the TBA field under scoring_breakdown to get calculations for (ex. totalPoints)

        Optional Parameters:
        calculations: list<str> = list of calculations to perform on a team's field values. mean, med, min, max, stdev, count. default=['mean']
        field_position_based: boolean = whether the field is categorized in TBA based on robot_position. default=False
        categorical_value: str = the categorical value to count. default=None
        exclude_playoffs: boolean = whether to exclude playoff matches from calculations. default = True
        event_key: str: = specify an event_key if you only want to perform calculations on matches played at a certain event. default=None

        Returns:
        calculated_statistics: dict = Dictionary of keys corresponding to the calculation name and values corresponding
        to the calculated value ex.) {mean: 77, max: 154, ...}
        """

        if team_key is None:
            print("A TBA team key is needed to perform this calculation")
            return

        return get_field_statistic(self.authkey, team_key, self.year, field_name, calculations,
                                    field_position_based,
                                    categorical_value,
                                    exclude_playoffs, event_key)

    def get_team_OPR_statistic(self, team_key, field='totalPoints', calculations=['mean'], exclude_playoffs=True):
        """
        Returns a dictionary of the mean/med/min/max/stdev/count of a team's OPR at every competition they've attended

        Parameters:
        team_key: str = the team key ('frc'+ TEAM_NUMBER) to get calculations for
        field: str = the TBA field to calculate contribution for. default='totalPoints'
        calculations: list<str> = list of calculations to perform on a team's field values. mean, med, min, max, stdev, count. default=['mean']
        exclude_playoffs: boolean = whether to exclude playoff matches from calculations. default = True

        Returns:

        calculated_statistics: dict = Dictionary of keys corresponding to the calculation name and
        values corresponding to their value ex.) {mean: 56, max: 56, ...}
        """
        if team_key is None:
            print("A TBA team key is needed to perform this calculation")
            return

        # List of tuples of format (event_key, event_CC for team)
        all_event_CCs = []
        for event in self.tba.team_events(team=team_key, year=self.year, keys=True):
            # Only calculate event CCs for events that have had matches
            if check_matches_exist(self.authkey, 2019, event_key=event, exclude_playoffs=exclude_playoffs):
                # HOTFIX: Events that aren't stored in TBA with standardized conventions (such as offseason events)
                # will break event OPR calculations. Such events will be skipped over
                try:
                    event_CCs = event_OPR(self.authkey, event, field, exclude_playoffs)
                except:
                    print("Error in calculating CCs for event_key:", event)
                    continue
                # Skip over any teams that didn't play any matches in their event
                try:
                    all_event_CCs.append((event, event_CCs.calculate_contribution()[team_key]))
                except KeyError:
                    print("Team: ", team_key, "didn't play any matches")
                    continue
            else:
                continue

        # Associates a calculation keyword to its appropriate function
        calculation_map = {'mean': mean, 'med': median, 'max': max, 'min': min, 'stdev': stdev, 'count': len}

        # Dictionary of {calculation keyword:value} pairs to be returned
        calculated_statistics = {}

        # Perform statistical calculations on list of event CCs
        for calculation in calculations:
            try:
                calculated_statistics[calculation] = calculation_map[calculation]([x[1] for x in all_event_CCs])
            except:
                print(
                    "Make sure your calculation is either max, min, mean, med, count, or stdev. If using stdev, there may not be more than 1 event CC yet")

        return calculated_statistics

    def get_event_field_statistics(self, event_key, field_name, calculations=['mean'], field_position_based=False,
                                    categorical_value=None,
                                    exclude_playoffs=True):
        """
        Returns a dictionary of calculated statistics (mean/med/min/max/stdev/count) for a given field (ex. totalPoints)
        for all teams at an event

        Required Parameters:
        event_key: str: = the event to get team field statistics from
        field_name: str = the TBA field under scoring_breakdown to get calculations for (ex. totalPoints)

        Optional Parameters:
        calculations: list<str> = list of calculations to perform on a team's field values. mean, med, min, max, stdev, count. default=['mean']
        field_position_based: boolean = whether the field is categorized in TBA based on robot_position. default=False
        categorical_value: str = the categorical value to count. default=None
        exclude_playoffs: boolean = whether to exclude playoff matches from calculations. default = True

        Returns:
        calculated_event_statistics: dict = Returns (possibly nested) dictionary holding the calculated statistic(s)
        for a given field for each team at the event.
        If field is position based, team_keys are keys. ex.) {'frc2521': 0.76, ...}
        If not, Outer key is the calculation name and inner keys are team keys ex.) {mean: {'frc2521': 100, ...}}
        """

        if event_key is None:
            print("A TBA event key is needed to perform this calculation")
            return

        if field_position_based and len(calculations) > 1:
            print(
                f"A a list of calculations {calculations} was given but only the proportion of times that the"
                f" categorical_value was recorded in each of the teams' matches will be returned")

        tba = TBA(self.authkey)

        event_team_keys = [team.key for team in tba.event_teams(event_key, simple=True)]

        # Creates (maybe nested) dictionary holding the calculated statistic(s) for a given field for each team at the event
        all_teams_statistics = dict.fromkeys(calculations, {}) if not field_position_based else dict()
        for team_key in event_team_keys:
            calculated_statistics = get_field_statistic(self.authkey, team_key, self.year, field_name,
                                                         calculations,
                                                         field_position_based,
                                                         categorical_value,
                                                         exclude_playoffs, event_key=event_key)
            if field_position_based:
                all_teams_statistics[team_key] = calculated_statistics
            else:
                for calculation_type in calculated_statistics.keys():
                    all_teams_statistics[calculation_type][team_key] = calculated_statistics[calculation_type]

        return all_teams_statistics

    def get_event_OPRs(self, event_key, field='totalPoints', exclude_playoffs=True):
        """
        Returns a dictionary containing the OPR of all teams at an event.

        Parameters:
        event_key: str: = the event to get team OPRs from
        field: str = the TBA/FIRSTApi field to calculate contribution for. default='totalPoints'
        Changing this will result in something other than OPRs being returned. Don't touch unless you know what you're doing
        exclude_playoffs: boolean = whether to exclude playoff matches from calculations. default = True

        Returns:

        calculated_contributions: dictionary = Keys are TBA team_keys with values being the team's OPR at the event
        ex.) {frc2521: 65, frc254: 148, ...}
        """
        if event_key is None:
            print("A TBA event key is needed to perform this calculation")
            return

        event_CCs = event_OPR(self.authkey, event_key, field, exclude_playoffs)
        return event_CCs.calculate_contribution()
