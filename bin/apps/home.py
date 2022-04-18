import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

index_page = html.Div([
    html.H1('PHX Dashboard Links'),
    html.Div([
        html.H4('Machine Status Tables'),
        dcc.Link('NALA', href='/apps/vmTblNALA'),
        html.Br(),
        dcc.Link('APAC', href='/apps/vmTblAPAC'),
    ]),
    html.Div([
        html.H4('Test Results'),
        dcc.Link('ABE', href='/apps/testReport')
    ]),
    html.Div([
        html.H4('VM Host Information'),
        dcc.Link('Usage Dashboard', href='/apps/vmHostInfo')
    ])
])
