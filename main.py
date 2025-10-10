from datetime import date, datetime

from dash import Dash, html, dcc, Input, callback, Output
import numpy as np
from yfinance_interface import get_stock_data
from plots_interface import fig_indicators, fig_main_plot
from calculations import max_profit
from lstm import lstm
#fig_indicators(data, max_prof).show()
#fig_line_plot(data, 'AMZN', buy_day, sell_day).show()

# Default datas:
ticker = "AMZN"
start_date = '1990-01-01'
end_date = '2024-08-01'

app = Dash()
app.layout = html.Div(children=[
    html.H1(children='Stock trend'),

    html.Div(children='''
        View stock trends right here and now.
    '''),

    html.Br(),
        html.Label('Ticker: '),
        dcc.Input(id='ticker', value=ticker, type='text'),

    html.Br(),
    html.Label('Date Start'),
    dcc.DatePickerSingle(
        id='start_date', 
        month_format='MMM Do, YY',
        placeholder='MMM Do, YY',
        date=date(1990,1,1)
    ),

    html.Br(),
    html.Label('Date End'),
    dcc.DatePickerSingle(
        id='end_date',   
        month_format='MMM Do, YY',
        placeholder='MMM Do, YY',
        date=date.today()
    ),

    html.Br(),
        html.Label('SMA Window (days)'),
        dcc.Slider(
            min=0,
            max=50,
            step=None,
            marks={i: str(i) for i in range(1, 51)},
            value=5,
            id="sma_window"
        ),

    dcc.Dropdown(
        id='return_type',
        options=[
            {'label': 'Simple Returns', 'value': 'simple'},
            {'label': 'Log Returns', 'value': 'log'},
        ],
        value='simple',  # default value
        clearable=False,
        style={'width': '200px'}
    ),
    
    # Uses ID to identify graph for callback. 
    # Replaces the section with the associated graph 
    dcc.Graph(
        id='main_graph',
    ),

    dcc.Graph(
        id='indicator_graph',
    ),
])

@callback(
    Output('main_graph', 'figure'),
    Output('indicator_graph', 'figure'),
    Input('ticker', 'value'),
    Input('start_date', 'date'),
    Input('end_date', 'date'),
    Input('sma_window', 'value'),
    Input('return_type', 'value')
    )
def update_line_fig(ticker, start_date, end_date, sma_window, return_type):
    data = get_stock_data(ticker, start_date, end_date)         # Fetch stock data
    if data is None or data.empty:
        from plotly import graph_objs as go
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No data available for this selection.")
        return empty_fig, empty_fig
    max_prof, sell_date, buy_date = max_profit(data)
    return fig_main_plot(data, ticker, buy_date, sell_date, int(sma_window), return_type), fig_indicators(data, max_prof, return_type)  # ADD return_type here

if __name__ == '__main__':
    app.run(host="127.0.0.1",debug=True)