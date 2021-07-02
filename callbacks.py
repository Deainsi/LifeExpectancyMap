import dash
import plotly.express as px
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

from app import app
from layouts import df


@app.callback(Output('YD', 'figure'),
              Input('LEM', 'hoverData'),
              Input('dropdown', 'value'))
def update_figure(countryd, country):
    ctx = dash.callback_context

    input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if input_id == 'LEM':
        cntr = countryd['points'][0]['hovertext']
    elif input_id == 'dropdown':
        cntr = country
    else:
        raise PreventUpdate

    cdf = df[df['Country'] == cntr]

    fig = px.line(cdf, x="Year", y="Value", color="Sex", title=cntr,
                  labels={'Value': 'Life expectancy'})

    fig.update_layout(yaxis={'zeroline': False},
                      xaxis={'zeroline': False},
                      hovermode='x',
                      plot_bgcolor="#afd3de")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig
