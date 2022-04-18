import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import io
import pandas as pd
import numpy as np
import os
import plotly.express as px
import datetime
from urllib import parse
from app import app

basePath = 'C:\\PhoenixControl\\MissionControl\\dataRepo'
def serve_summarylayout(paramString):
    paramDict = parse.parse_qs(parse.urlsplit(paramString).query)
    machineName = paramDict['machineName'][0]
    date = paramDict['date'][0]
    f = io.open(f'{basePath}\\{machineName}\\logFiles\\{date}_{machineName}_phxSummary.log', mode="r", encoding="utf-16")
    rawString = f.read()
    return html.Div(rawString, style={'line-height': '1.25', 'font-family': 'monospace', 'whiteSpace': 'pre'})