import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import os
import plotly.express as px
import datetime
from app import app

# PHX data repo and config files
dataRepo = 'C:\\PhoenixControl\\MissionControl\\dataRepo'
config = 'C:\\PhoenixControl\\MissionControl\\configFiles\\phxConfig.csv'
# Get configs
configDF = pd.read_csv(config)

# Buld the data frame using current date as default
def build_DataFrames():
    # Get current date
    formattedDate = datetime.datetime.now().strftime("%Y_%m_%d")
    
    # Empty df
    mainDF = pd.DataFrame(columns=['Machine', 'Operating System', 'Media', 'Install Test', 'Legacy API', 'Web API', 'SIO Validation'])
    indexNum = 0
    for machine in configDF['vmNameDNS']:
        # Get machine name
        machineName = machine.split('.')[0]
        # get paths year_month_day
        resultsPath = f'{dataRepo}\\{machineName}\\detailedResults\\{formattedDate}_testResults'
        envInfoPath = f'{resultsPath}\\envInfo.csv'
        launchTestPath = f'{resultsPath}\\Results_LaunchTest.csv'
        legacyAPIPath = f'{resultsPath}\\{formattedDate}_ResultsApiSummary.csv'
        webAPIPath = f'{resultsPath}\\{formattedDate}_ResultsWebApiSummary.csv'
        sioValPath = f'{resultsPath}\\sioValidation.val'
        if os.path.isfile(envInfoPath) and os.path.isfile(launchTestPath) and os.path.isfile(legacyAPIPath) and os.path.isfile(webAPIPath) and os.path.isfile(sioValPath):
            # Gather results)
            envInfoDF = pd.read_csv(envInfoPath)
            launchTestDF = pd.read_csv(launchTestPath)
            legacyAPIDF = pd.read_csv(legacyAPIPath)
            webAPIDF = pd.read_csv(webAPIPath)
            sioValDF = pd.read_csv(sioValPath)

            # Wash sio val for negative tests
            # sioValDF['Result'] = np.where((sioValDF.Result == 'FAIL' and sioValDF.Abe == 'Drive.Power'), 'PASS', sioValDF.Result)
            # sioValDF['Result'] = np.where((sioValDF.Result == 'FAIL' and sioValDF.Abe == 'Motors.Power'), 'PASS', sioValDF.Result)
            # sioValDF['Result'] = np.where((sioValDF.Result == 'FAIL' and sioValDF.Abe == 'Turbines.Power'), 'PASS', sioValDF.Result)
            # Get the suff
            intallTest = round((launchTestDF['result'].value_counts()['PASS']/launchTestDF['result'].count())*100, 2)
            legacyAPI = round((legacyAPIDF['Passed'].sum()/legacyAPIDF['Total'].sum())*100, 2)
            webAPI = round((webAPIDF['Passed'].sum()/webAPIDF['Total'].sum())*100, 2)
            sioVal = round((sioValDF['Result'].value_counts()['PASS']/sioValDF['Result'].count())*100, 2)
            # Append
            mainDF.loc[indexNum] = [machineName, envInfoDF['OsName'][0], envInfoDF['AspenMediaName'][0], intallTest, legacyAPI, webAPI, sioVal]
        else:
            mainDF.loc[indexNum] = [machineName, '-', '-', '-', '-', '-', '-']
        indexNum = indexNum + 1
    # Return df
    return mainDF

def generate_resultsTable():
    mainDF = build_DataFrames()
    return dash_table.DataTable(
        id='resultsTable',
        data=mainDF.to_dict('records'),
        sort_action='native',
        columns=[{"name": i, "id": i} for i in mainDF.columns],
        style_cell={'textAlign': 'left'},
        style_data_conditional=(
            [
                {
                    'if': {
                        'filter_query': '{{{}}} < {}'.format(col, 100),
                        'column_id': col
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                } for col in ['Install Test', 'Legacy API', 'Web API', 'SIO Validation']
            ] +
            [
                {
                    'if': {
                        'filter_query': '{{{}}} = {}'.format(col, 100),
                        'column_id': col
                    },
                    'backgroundColor': '#3D9970',
                    'color': 'white'
                } for col in ['Install Test', 'Legacy API', 'Web API', 'SIO Validation']
            ]
        )
    )

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H3(f'ABE Test Results - {datetime.datetime.now().strftime("%m/%d/%Y")}'),
                ],
            ),
        ],
    )

def generate_SummaryTable():
    formattedDate = datetime.datetime.now().strftime("%Y_%m_%d")
    return html.Table([
        html.Thead(
            html.Tr([html.Th('Test Summary Links')])
        ),
        html.Tbody([
            html.Tr([
                html.Td(html.A(configDF.iloc[i]['vmNameDNS'].split('.')[0], href=f'/apps/testSummary?date={formattedDate}&machineName={configDF.iloc[i]["vmNameDNS"].split(".")[0]}', target="_blank"))
            ]) for i in range(len(configDF))
        ])
    ])

def serve_layout():
    #return html.H1('The time is: ' + str(datetime.datetime.now()))
    # return html.Div(
    #     html.Div([build_banner()])
    #     html.Div([generate_resultsTable()], style={'display': 'inline-block', 'padding': '5px'}),
    #     )
    return html.Div(
        id="big-app-container",
        children=[
            build_banner(),
            # dcc.Interval(
            #     id="interval-componentTR",
            #     interval=2 * 1000,  # in milliseconds
            #     n_intervals=50,  # start at batch 50
            #     disabled=True,
            # ),
            html.Div(
                #generate_vmTable()
                id="app-container",
                children=[
                    # Main app
                    #html.Div(id="app-contentTR"),
                    html.Div([
                        html.Div([generate_resultsTable()], style={'display': 'inline-block', 'padding': '5px'}),
                        html.Div([generate_SummaryTable()]), 
                    ]),
                ],
            ),
            # # Load tab contents
            # dcc.Store(id="n-interval-stage", data=50),
            # #generate_modal(),
        ],
    )

#layout = serve_layout

# @app.callback(
#     [Output("app-contentTR", "children"), Output("interval-componentTR", "n_intervals")],
#     [Input("dateTime", "value")],
#     [State("n-interval-stage", "data")],
# )
# def render_content(stopped_interval):  
#     return (
#         html.Div([
#             html.Div([
#                 html.Div([generate_resultsTable()], style={'display': 'inline-block', 'padding': '5px'}), 
#                 ]),
#             ]),
#         stopped_interval,
#     )