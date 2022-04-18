import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

from app import app

# VM host spreadsheet location
hostSpreadSheet = 'C:\\Users\\bardend\\OneDrive - Aspen Technology, Inc\\QE VM Hosts\\VM list.xlsx'

def build_DataFrames(tab_switch):
    hostCSVPath = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\user_{tab_switch}.csv'
    hyperVReportPath = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\hyperV_{tab_switch}.csv'
    driveReportPath = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\diskInfo_{tab_switch}.csv'
    # Import
    hostCSVDF = pd.read_csv(hostCSVPath)
    hyperVReportDF = pd.read_csv(hyperVReportPath)
    driveReportDF = pd.read_csv(driveReportPath)
    # Make dfs
    vmTableDF = pd.merge(hostCSVDF, hyperVReportDF, on=['VM Name'], how='outer')
    masterTableDF = pd.merge(vmTableDF, driveReportDF, on=['Drive'], how='outer')
    vmTableDF = pd.merge(vmTableDF, driveReportDF, on=['Drive'], how='inner')
    vmTableDF['Usage %'] = vmTableDF['VM Size (GB)']/vmTableDF['Drive Size (GB)']*100
    vmTableDF = vmTableDF.drop(columns=['Free Space (GB)','Drive Size (GB)'])
    # Return dfs
    return {"vmTableDF": vmTableDF, "masterTableDF": masterTableDF, "driveReportDF": driveReportDF}
    

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H3("VM Host Information"),
                    html.A('Sharepoint Spreadsheet - (The content of this page is refreshed once a day. Changes will take time to show up.)', href='https://asptechinc-my.sharepoint.com/:x:/g/personal/ryan_barden_aspentech_com/EcY11v7SaYFFlpS1MKy-9OoB7u4ZrsQ5pfR2hXLDKo2eBg?e=rhdkx0', target="_blank"),
                ],
            ),
        ],
    )

def generateTabChild(name):
    return dcc.Tab(
        id=f'{name}-tab',
        label=f'{name}',
        value=f'{name}',
        className="custom-tab",
        selected_className="custom-tab--selected",
        )

def build_tabs():
    df = pd.read_excel(hostSpreadSheet, sheet_name=None)
    hostList = df.keys()
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[generateTabChild(host) for host in hostList],
            )
        ],
    )

def generate_vmTable(tab_switch):
    hostSpreadSheet = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\user_{tab_switch}.csv'
    hyperVReportPath = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\hyperV_{tab_switch}.csv'
    driveReportPath = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\diskInfo_{tab_switch}.csv'
    #spreadSheet = pd.read_excel(hostSpreadSheet, sheet_name=None)
    spreadSheet = pd.read_csv(hostSpreadSheet)
    hyperVReport = pd.read_csv(hyperVReportPath)
    driveReport = pd.read_csv(driveReportPath)
    #df = pd.merge(spreadSheet[tab_switch], hyperVReport, on=['VM Name'], how='outer')
    df = pd.merge(spreadSheet, hyperVReport, on=['VM Name'], how='outer')
    #driveReport[driveReport['Drive'] == Drive]['Drive Size (GB)']
    #df['% Of Drive'] = df['VM Size (GB)']/df['Drive Size (GB)']*100
    #df = spreadSheet[tab_switch]
    return dash_table.DataTable(
        id='vmTable',
        data=df.to_dict('records'),
        sort_action='native',
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left'},
        style_data_conditional=(
            [
                {
                    'if': {
                        'filter_query': '{{{}}} is blank'.format(col),
                        'column_id': col
                    },
                    'backgroundColor': 'tomato',
                    'color': 'white'
                } for col in df.columns
            ]
        )
    )

def generate_BarPie(tabName):
    dfs = build_DataFrames(tabName)
    driveReportDF = dfs['driveReportDF']
    masterTableDF = dfs['masterTableDF']
    masterTableDF['Group'] = masterTableDF.fillna('Other')['Group']
    masterTableDF['VM Size (GB)'] = masterTableDF.fillna(int("0"))['VM Size (GB)']

    # Get total VM by drive
    totalVMSDrive = masterTableDF.groupby(["Drive"]).sum()['VM Size (GB)']

    # Append missing data label as other
    for drive in totalVMSDrive.index:
        usedOther = float(driveReportDF[driveReportDF['Drive'] == drive]['Drive Size (GB)'] - driveReportDF[driveReportDF['Drive'] == drive]['Free Space (GB)'] - totalVMSDrive[drive])
        driveTotal = float(driveReportDF[driveReportDF['Drive'] == drive]['Drive Size (GB)'])
        masterTableDF = masterTableDF.append(pd.DataFrame([[drive, "Other", usedOther, driveTotal]], columns=['Drive', 'Group', 'VM Size (GB)', 'Drive Size (GB)']))
    masterTableDF['Usage %'] = masterTableDF['VM Size (GB)']/masterTableDF['Drive Size (GB)']*100

    # Create pie df
    pieDF = pd.DataFrame()
    totalResurces = driveReportDF.sum()['Drive Size (GB)']
    totalGroupUseSeries = masterTableDF.groupby(["Group"]).sum()['VM Size (GB)']
    for group in totalGroupUseSeries.index:
        pieDF = pieDF.append(pd.DataFrame([[group, totalGroupUseSeries[group]]], columns=['Group', 'Usage (GB)']))
    pieDF = pieDF.append(pd.DataFrame([["Free", totalResurces - pieDF.sum()['Usage (GB)']]], columns=['Group', 'Usage (GB)']))

    figBar = px.bar(masterTableDF, x="Drive", y="Usage %", color="Group", title="Usage By Disk", hover_name="VM Name")
    figBar.update_yaxes(range=[0, 100])
    figPie = px.pie(pieDF, values='Usage (GB)', names='Group', title="Total Storage Use")
    return dcc.Graph(id='bar-graph', figure=figBar), dcc.Graph(id='pie-chart', figure=figPie)



def generate_adminsTable(tabName):
    adminList = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\adminList_{tabName}.csv'
    df = pd.read_csv(adminList)
    return dash_table.DataTable(
        id='adminsTable',
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left'},
        data=df.to_dict('records'),
    )

def generate_otherTable(tabName):
    otherCSV = f'C:\\Users\\BARDEND\\Desktop\\newDash\\data\\otherFiles_{tabName}.csv'
    df = pd.read_csv(otherCSV)
    return dash_table.DataTable(
        id='otherTable',
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left'},
        data=df.to_dict('records'),
    )

def generateLandingText():
    return html.Div(
        className="markdown-text",
        children=dcc.Markdown(
            children=(
                """
        ###### VM Host Resource Snapshot
        Click on any of the above tabs to see resource and VM information for that machine.
                """
            )
        ),
    ) 


# change to app.layout if running as single page app instead
layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=50,  # start at batch 50
            disabled=True,
        ),
        html.Div(
            #generate_vmTable()
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        # Load tab contents
        dcc.Store(id="n-interval-stage", data=50),
        #generate_modal(),
    ],
)

@app.callback(
    [Output("app-content", "children"), Output("interval-component", "n_intervals")],
    [Input("app-tabs", "value")],
    [State("n-interval-stage", "data")],
)
def render_tab_content(tab_switch, stopped_interval):
    if tab_switch == 'tab2':
        return (
            generateLandingText(),
            stopped_interval,
        )
    else:
        bar, pie = generate_BarPie(tab_switch)     
        return (
            html.Div([
                html.Div([
                    html.A('Live Resource Monitor', href=f'http://{tab_switch}:62208', target="_blank"),
                    html.Br(),
                    
                    html.Div([bar], style={'display': 'inline-block', 'padding': '5px'}),
                    html.Div([pie], style={'display': 'inline-block', 'padding': '5px'}),
                    ]),
                html.Div([
                    html.Div([generate_vmTable(tab_switch)], style={'display': 'inline-block', 'padding': '5px'}), 
                    html.Div([generate_adminsTable(tab_switch)], style={'display': 'inline-block', 'padding': '5px'}),
                    html.Div([generate_otherTable(tab_switch)], style={'display': 'inline-block', 'padding': '5px'}),
                    ]),
                ]),
            stopped_interval,
        )
