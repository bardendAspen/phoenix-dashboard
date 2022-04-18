import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import home, vmTblNALA, vmTblAPAC, vmHostInfo, testReport, testSummary, deploymentStatus, waveInfo


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              Input('url', 'search'))
def display_page(pathname, search):
    if pathname == '/apps/vmTblNALA':
        return vmTblNALA.layout
    elif pathname == '/apps/vmTblAPAC':
        return vmTblAPAC.layout
    elif pathname == '/apps/vmHostInfo':
        return vmHostInfo.layout
    elif pathname == '/apps/testReport':
        testReport.layout = testReport.serve_layout()
        return testReport.layout
    elif pathname == '/apps/testSummary':
        testSummary.layout = testSummary.serve_summarylayout(search)
        return testSummary.layout
    elif pathname == '/apps/deploymentStatus':
        deploymentStatus.layout = deploymentStatus.serve_summarylayout(search)
        return deploymentStatus.layout
    elif pathname == '/wave':
        return waveInfo.layout
    else:
        return home.index_page

if __name__ == '__main__':
    app.run_server(debug=True,port=8050,host='0.0.0.0')