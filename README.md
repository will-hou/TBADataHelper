Needs name change

To Do

A simple package used to perform aggregate and OPR calculations on FRC match data

# Installation
Make sure you have a TBA Auth Key. Learn what this is and how to get one [here](https://www.thebluealliance.com/apidocs)


1. Run `git clone https://github.com/will-hou/TBADataFetcher.git` in a directory of your choice
2. Move the `TBADataFetcher` folder into the project directory you plan on using it in

Example file structure:
```
MyAnalyticsProgram>
    TBADataFetcher
    __init__.py
    run.py
    README.md
```

# Usage

To create an instance of the TBAFetcher class:
```
fetcher = TBA('###YOUR_AUTHKEY_HERE###', year)
```
`TBADataFetcher` constructor also takes two optional parameters:

### team_key:
The string `'frc'` + the string `'team_number'` ex.) `'frc2521'`

#### `fetcher.get_metric_statistic`:  
Returns a dictionary of calculated statistics mean/min/max/stdev/count for a given metric (ex. totalPoints)
#### `fetcher.get_team_OPR_statistic`:
Returns a dictionary of the mean/med/min/max/stdev/count of a team's OPR at every competition they've attended that year

### event_key: 
The TBA event key for an event. Can be found in the website event url after `event/` ex.) `'2020orore'` 

#### `get_event_metric_statistics`:
Returns a dictionary of calculated statistics mean/med/min/max/stdev/count for a given metric (ex. totalPoints)
for all teams at an event
#### `get_event_OPRs`:
Returns a dictionary containing the OPR of all teams at an event.

## Example Usages
