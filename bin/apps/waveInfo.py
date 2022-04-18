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

filePath = 'F:\\AspenPackageRepo\\wave\\README.md'

with io.open(filePath, mode="r") as f:
    rawString = f.read()

layout = dcc.Markdown(rawString)
