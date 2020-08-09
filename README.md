Needs name change

To Do

A simple package used to perform aggregate and OPR calculations on FRC match data

## Installation
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

## Usage

To create an instance of the TBAFetcher class:
```
fetcher = TBA('###YOUR_AUTHKEY_HERE###')
```
