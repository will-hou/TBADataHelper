A simple package used to perform aggregate and OPR calculations on FRC match data collected in 2016 and onwards.

# Installation
Make sure you have a TBA Auth Key. Learn what this is and how to get one [here](https://www.thebluealliance.com/apidocs)

1. Run `git clone https://github.com/will-hou/TBADataHelper.git` in a directory of your choice
2. Move the `TBADataHelper` folder into the project directory you plan on using it in

Example file structure:
```
├── MyAnalyticsProgram
├── TBADataHelper
    ├──... 
├── __init__.py
├── run.py
└── README.md
```

TBADataHelper uses [tbapy](https://github.com/frc1418/tbapy) to make requests to the TBA API v3. Make sure that package is installed in addition to [numpy](https://github.com/numpy/numpy) 

# Usage

To create an instance of the TBADataHelper class:
```
fetcher = TBADataHelper('###YOUR_AUTHKEY_HERE###', year)
fetcher = TBADataHelper('###MY_AUTHKEY###', 2020)
```
### Methods taking a team_key:
The string `'frc'` + the string `'team_number'` ex.) `'frc2521'`

#### `fetcher.get_team_field_statistic()`:  
Returns a dictionary of calculated statistics (mean/med/min/max/stdev/count) for a given field (ex. totalPoints)
#### `fetcher.get_team_OPR_statistic()`:
Returns a dictionary of the mean/med/min/max/stdev/count of a team's OPR at every competition they've attended that year

### Methods taking an event_key: 
The TBA event key for an event. Can be found in the website event url after `event/` ex.) `'2020orore'` 

#### `fetcher.get_event_field_statistics()`:
Returns a dictionary of calculated statistics (mean/med/min/max/stdev/count) for a given field (ex. totalPoints)
for all teams at an event
#### `fetcher.get_event_OPRs()`:
Returns a dictionary containing the OPR of all teams at an event.

#### Read more about specific method arguments using help() or looking at examples below

# Example Usages

### Print all team OPRs at an event in descending order
```
# Calculate the OPR of all teams competing in the PNW District Clackamas Academy Event 2020.
event_OPRs = fetcher.get_event_OPRs(event_key='2020orore')
# Store the team key and their OPR as a list of tuples
event_OPRs = [(team, OPR) for team, OPR in event_OPRs.items()]
# Sort the OPRs in descending order so teams with the highest OPR are printed at the top
event_OPRs.sort(key=lambda x: x[1], reverse=True)
# Print each team and their OPR to the console
for team, OPR in event_OPRs:
    print(f"{team}: {OPR}")
```

Output:
```
frc1540: 89.15983286702696
frc2471: 79.21925967645967
...
frc3024: -5.022913277675411
```

### Print how often each team at an event climbed sucessfully  
```
# Count the proportion of times "Hang" was recorded as the endgame state in all matches played by each team at the PNW District Clackamas Academy Event 2020.
event_climb_props = fetcher.get_event_field_statistics(event_key='2020orore', field_name='endgameRobot',
                                                        field_position_based=True, categorical_value='Hang',
                                                        exclude_playoffs=False)
# Store the team key and their climb proportion as a list of tuples
event_climb_props = [(team, prop) for team, prop in event_climb_props.items()]
# Sort the proportions in descending order so teams that climb most frequently are printed near the top
event_climb_props.sort(key=lambda x: x[1], reverse=True)
# Print each team and their climb proportion to the console
for team, prop in event_climb_props:
    print(f"{team}: {prop}")
```
Output:
```
frc3674: 0.947
frc2990: 0.875
...
frc847: 0.0
```
Possible categorical values (found on [FIRST Events API](https://frcevents2.docs.apiary.io/#/reference/match-results/score-details)): <br/>
**2020:** Unknown, None, Park, Hang <br/>
**2019:** Unknown, None, HabLevel1, HabLevel2, HabLevel3 <br/>
**2018:** Unknown, None, Parking, Climbing, Levitate <br/>

 `get_team_field_statistics()` assumes that robot endgame states are categorized using the `endgameRobot#` convention used by the FIRST API after 2018. As such, there is currently no support for climb data in games before PowerUp.
 
 ### Print the minimum, maximum, and average number of points scored by the team's alliance in all their matches
 ```
# Set up the fetcher to only include data from 2018 matches
fetcher = TBADataHelper('###MY_AUTHKEY###', 2018)
# Calculate the min, max, and mean statistics for the totalPoints value across all matches
team_min_max_mean_total_points = fetcher.get_team_field_statistics(team_key='frc2521', field_name='totalPoints',
                                                                    exclude_playoffs=False,
                                                                    calculations=['min', 'max', 'mean'])
# Log the dictionary of statistics to the console
print(team_min_max_mean_total_points)
```
Outputs:
```
{'min': 66, 'max': 469, 'mean': 309.94736842105266}
```

### Notes/Contributing/Bug Reports:
The majority of this package was written in a bit of a rush during the 2018 build season. The methods have been tested fairly
rigorously for accuracy but I can't guarantee a 100% bug-free experience, especially if you're trying to aggregate data
from offseason events included in TBA. I don't plan on adding any  new features at this time but will respond to any
specific questions or concerns. Or maybe you're actually interested in expanding this project! Whatever it is feel free 
to send me a message. 

Happy Analyzing! :D 