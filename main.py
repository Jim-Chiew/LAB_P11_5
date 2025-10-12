from datetime import date
from dash import Dash, html, dcc, Input, callback, Output
from pandas import to_datetime
from yfinance_interface import get_stock_data
from plots_interface import fig_main_plot, fig_indicators, error_page
from calculations import max_profit_edge_case

# Default datas:
ticker = "AMZN"

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
        month_format='Do MMM, YY',
        placeholder='Do MMM, YY',
        date=date(2024,1,1),
        display_format="DD/MM/YYYY"
    ),

    html.Br(),
    html.Label('Date End'),
    dcc.DatePickerSingle(
        id='end_date',   
        month_format='Do MMM, YY',
        placeholder='Do MMM, YY',
        date=date(2024,1,31),
        display_format="DD/MM/YYYY"
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
    

    # Uses ID to identify graph for callback. 
    # Replaces the section with the associated graph 
    dcc.Graph(
        id='main_graph',
    ),

    
    dcc.Graph(
        id='indicator_graph',
    ),



    html.P([    
    "1. Count of up/down trend: Number of consecutive upward or downward trends. A sequence of 2 or more days moving in the same direction (upward or downward) counts as 1 trend.", html.Br(),
    "2. Highest count of up/down day in a single trend: The longest streak of consecutive upward or downward days in a single trend."]
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
    data = get_stock_data(ticker, start_date, end_date)
    result = max_profit_edge_case(data)

    start_date_datetime = to_datetime(start_date)
    end_date_datetime = to_datetime(end_date)
    delta_days = (end_date_datetime - start_date_datetime).days + 1  # Inclusive
    if delta_days < sma_window:         # Check if SMA window > date range
        return error_page(f"Selected range is {delta_days} days, but SMA window is {sma_window} days. Please choose a smaller SMA window or a larger date range."), error_page("")
   
    return fig_main_plot(data, ticker, result, int(sma_window), return_type), fig_indicators(data, result['max_profit_single'])

if __name__ == '__main__':
    app.run(host="127.0.0.1",debug=True)