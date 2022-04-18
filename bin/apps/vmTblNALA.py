import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
from app import app

## PXH Configs ##
phxConfig = 'C:\PhoenixControl\MissionControl\configFiles\phxConfig.csv'
dataPath = 'C:\PhoenixControl\MissionControl\dataRepo'
#################

# Import Current Configuration
conf = pd.read_csv(phxConfig)

def getStatus(configDF):
    # Empty holder
    statusDF = []
    # Build Table
    for vm in conf['vmNameDNS']:
        name = vm.split('.')[0]
        status = f'{dataPath}\\{name}\\status.csv'
        users = f'{dataPath}\\{name}\\users.csv'
        # Get status
        if os.path.exists(status):
            df = pd.read_csv(status, index_col=None, header=0, encoding='UTF-16')
        else:
            df = pd.DataFrame()
        # Get users
        if os.path.exists(users):
            dfU = pd.read_csv(users, index_col=None, header=0, encoding='UTF-16')
        else:
            dfU = pd.DataFrame()
        statusDF.append(df.join(dfU))
    return pd.concat(statusDF, axis=0, ignore_index=True)

def generate_table(dataframe, max_rows=50):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

def generate_thread(dataframe, max_rows=50):
    return html.Thead(
        html.Tr([html.Th(col) for col in dataframe.columns])
    ),
    html.Tbody([
        html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))
    ])

tableDF = getStatus(conf)

layout = html.Div(children=[
    html.H4(children='PHX Machine Status Dashboard - NALA'),
    html.Div(id='live-update-table-NALA'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
    ),
    html.Br(),
    dcc.Link('PHX Home', href='/apps/home')
])

@app.callback(Output('live-update-table-NALA', 'children'), [Input('interval-component', 'n_intervals')])   
def update_table(n):   
    newDF = getStatus(conf)
    return [generate_table(newDF)]
