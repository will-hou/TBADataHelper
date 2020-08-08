from .functions import *
from .opr import *
from tbapy import TBA
from statistics import stdev


class TBADataFetcher:
    """
    Main class for fetching data and analytics from TBA

    Required constructor arguments:
    year: int = The year to get data from

    Optional constructor arguments:
    team_key: str = The TBA key for a team. Equal to 'frc+[team_number]'
                    Required for the get_metric_average and get_team_CC methods
    event_key: str = The TBA key for an event
                    Required for the get_event_CCs method
    """

    def __init__(self, authkey, year, team_key=None, event_key=None):
        self.authkey = authkey
        self.year = year

        # Optional Parameters
        self.team_key = team_key
        self.event_key = event_key

        # TBA data handler
        self.tba = TBA(authkey)

    def get_metric_statistic(self, metric_name, calculations=['mean'], metric_position_based=False,
                             categorical_value=None,
                             exclude_playoffs=True):
        """
        Returns a dictionary of calculated statistics (mean/min/max/stdev/count) for a given metric (ex. totalPoints)

        - If the metric is categorized in TBA based on robot position(ex. endgameRobot2, etc.), the metric_position_based
        and categorical_value parameters need to be specified. The percentage of times that categorical_value was recorded
        for the team will be returned in decimal form.

        Required Parameters:
        metric_name: str = the TBA metric under scoring_breakdown to get calculations for (ex. totalPoints)

        Optional Parameters:
        calculations: list<str> = list of calculations to perform on a team's metric values. max, min, mean, stdev, count. default=['mean']
        metric_position_based: boolean = whether the metric is categorized in TBA based on robot_position. default=False
        categorical_value: str = the categorical value to get averages by. default=None
        exclude_playoffs: boolean = whether to exclude playoff matches from calculations. default = True

        Returns:
        calculated_statistics: dict = Dictionary of keys corresponding to the calculation name and values corresponding
        to the calculated value ex.) {mean: 77, max: 154, ...}
        """

        if self.team_key is None:
            print("A TBA team key is needed to perform this calculation")
            return

        return get_metric_statistic(self.authkey, self.team_key, self.year, metric_name, calculations,
                                    metric_position_based,
                                    categorical_value,
                                    exclude_playoffs)

    def get_team_event_OPR_statistic(self, metric='totalPoints', calculations=['mean'], exclude_playoffs=True):
        """
        Calculates the max/min/mean/count/stdev of a team's OPR at every competition they've attended

        Parameters:

        metric: str = the TBA/FIRSTApi metric to calculate contribution for. default='totalPoints'
        calculations: list<str> = list of calculations to perform on a team's event OPR. max, min, mean, stdev, count. default=['mean']
        exclude_playoffs: boolean = whether to exclude playoff matches from calculations. default = True

        Returns:

        calculated_statistics: dict = Dictionary of keys corresponding to the calculation name and
        values corresponding to their value ex.) {mean: 56, max: 56, ...}
        """

        if self.team_key is None:
            print("A TBA team key is needed to perform this calculation")
            return

        # List of tuples of format (event_key, event_CC for team)
        all_event_CCs = []
        for event in self.tba.team_events(team=self.team_key, year=self.year, keys=True):
            # Only calculate event CCs for events that have had matches
            if check_matches_exist(self.authkey, 2019, event_key=event, exclude_playoffs=exclude_playoffs):
                # HOTFIX: Events that aren't stored in TBA with standardized conventions will break event_CC calculations. Such events will be skipped over
                try:
                    event_CCs = event_OPR(self.authkey, event, metric, exclude_playoffs)
                except:
                    print("Error in calculating CCs for event_key:", event)
                    continue

                # Skip over any teams that didn't play any matches in their event
                try:
                    all_event_CCs.append((event, event_CCs.calculate_contribution()[self.team_key]))
                except KeyError:
                    print("Team: ", self.team_key, "didn't play any matches")
                    continue
            else:
                continue

        # Associates a calculation keyword to its appropriate function
        calculation_map = {'mean': mean, 'max': max, 'min': min, 'stdev': stdev, 'count': len}

        # Dictionary of {calcualtion keyword:value} pairs to be returned
        calculated_statistics = {}

        # Perform statistical calculations on list of event CCs
        for calculation in calculations:
            try:
                calculated_statistics[calculation] = calculation_map[calculation]([x[1] for x in all_event_CCs])
            except:
                print(
                    "Make sure your calculation is either max, min, mean, count, or stdev. If using stdev, there may not be more than 1 event CC yet")

        return calculated_statistics

    def get_event_metric_statistics(self, metric_name, calculations=['mean'], metric_position_based=False,
                                    categorical_value=None,
                                    exclude_playoffs=True):
        if self.event_key is None:
            print("A TBA event key is needed to perform this calculation")
            return

        tba = TBA(self.authkey)

        event_team_keys = [team.key for team in tba.event_teams(self.event_key, simple=True)]

        all_teams_statistics = dict.fromkeys(calculations, {}) if not metric_position_based else dict()

        for team_key in event_team_keys:
            calculated_statistics = get_metric_statistic(self.authkey, team_key, self.year, metric_name,
                                                         calculations,
                                                         metric_position_based,
                                                         categorical_value,
                                                         exclude_playoffs, event_key=self.event_key)
            if metric_position_based:
                all_teams_statistics[team_key] = calculated_statistics
            else:
                for calculation_type in calculated_statistics.keys():
                    all_teams_statistics[calculation_type][team_key] = calculated_statistics[calculation_type]

        return all_teams_statistics

    def get_event_OPRs(self, metric='totalPoints', exclude_playoffs=True):
        """
        Calculates the OPR of all the teams at an event.

        Parameters:

        metric: str = the TBA/FIRSTApi metric to calculate contribution for. default='totalPoints'
        Changing this will result in something other than OPRs being returned. Don't touch unless you know what you're doing
        exclude_playoffs: boolean = whether to exclude playoff matches from calculations. default = True

        Returns:

        calculated_contributions: dictionary = Keys are TBA team_keys with values being the team's OPR at the event
        ex.) {frc2521: 65, frc254: 148, ...}
        """
        if self.event_key is None:
            print("A TBA event key is needed to perform this calculation")
            return

        event_CCs = event_OPR(self.authkey, self.event_key, metric, exclude_playoffs)
        return event_CCs.calculate_contribution()
