import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import io
import pandas as pd
import numpy as np
import os
import plotly.express as px
from datetime import datetime
from urllib import parse
from app import app

# PHX data repo and config files
basePath = 'C:\\PhoenixControl\\MissionControl\\dataRepo'
config = 'C:\\PhoenixControl\\MissionControl\\configFiles\\phxConfig.csv'
# Get configs
configDF = pd.read_csv(config)

def formatDateTime(dateTimeString):
    dtList = dateTimeString.split(' ')
    mdyList = dtList[0].split('/')
    twofourTime = datetime.strftime(datetime.strptime(f'{dtList[1]} {dtList[2]}', "%I:%M:%S %p"), "%H:%M:%S")
    return f'{mdyList[2]}-{mdyList[0]}-{mdyList[1]} {twofourTime}'

def build_banner(date):
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H3(f'PHX Deployment Status - {datetime.strptime(date, "%Y_%m_%d").strftime("%m/%d/%Y")}'),
                ],
            ),
        ],
    )

def parseLogs(date):
    # Empty df
    ganttList = []
    for machine in configDF['vmNameDNS']:
        machineName = machine.split('.')[0]
        logFile = f'{basePath}\\{machineName}\\logFiles\\{date}_{machineName}_phxInstall.log'
        if os.path.isfile(logFile):
            # Open the file 
            with io.open(logFile, mode="r", encoding="utf-16") as f:
                lines = f.read().splitlines()
            parsingOn = False
            scriptName = None
            startTime = None
            finishTime = None
            status = 'In Progress'
            # Go through
            for line in lines:
                # Check if parsing is on 
                if parsingOn:
                    #parsimonious
                    if line == '***********************************************':
                        # Prep vars
                        finishTime = formatDateTime(finishTimeLine.split(' :: ')[1])
                        if status != 'Error Detected':
                            status = 'Complete'
                        # Drop a new element
                        ganttList.append(dict(Machine=machineName, Job=scriptName, Start=startTime, Finish=finishTime, Status=status))
                        # Flip the variables
                        parsingOn = False
                        scriptName = None
                        startTime = None
                        finishTime = None
                        status = 'In Progress'
                    elif '** Script:' in line:
                        scriptName = line.split(' ')[2]
                    elif '::' in line and startTime == None:
                        startTime = formatDateTime(line.split(' :: ')[1])
                    elif '::' in line and startTime != None:
                        finishTimeLine = line

                    # Look for error
                    if 'Error' in line or 'error' in line:
                        status = 'Error Detected'
                else:
                    if line == '***********************************************':
                        # Turn parsing on
                        parsingOn = True
            # Check for unfinished
            if parsingOn:
                finishTime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                ganttList.append(dict(Machine=machineName, Job=scriptName, Start=startTime, Finish=finishTime, Status=status))

    return pd.DataFrame(ganttList)

def serve_summarylayout(paramString):
    # Dealy with query string
    # Get the date
    paramDict = parse.parse_qs(parse.urlsplit(paramString).query)
    if 'date' in paramDict.keys():
        date = paramDict['date'][0]
    else:
        date = datetime.strftime(datetime.now(), "%Y_%m_%d")
    # Build it out
    ganttDF = parseLogs(date)
    colors = {'Error Detected': 'red',
              'In Progress': 'goldenrod',
              'Complete': 'green'}
    ganttFig = px.timeline(ganttDF, x_start="Start", x_end="Finish", y="Machine", color='Status', color_discrete_map=colors, hover_name="Job")
    return html.Div(
        id="big-app-container",
        children=[
            build_banner(date),
            html.Div(
                id="app-container",
                children=[
                    html.Div([
                        html.Div(dcc.Graph(id='gantt', figure=ganttFig)),
                    ]),
                ],
            ),
        ],
    ) 
    