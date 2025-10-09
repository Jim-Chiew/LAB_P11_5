from datetime import date
from dash import Dash, html, dcc, Input, callback, Output
from yfinance_interface import get_stock_data
from plots_interface import fig_main_plot, fig_indicators
from calculations import max_profit

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
    data = get_stock_data(ticker, start_date, end_date)
    max_prof, sell_date, buy_date = max_profit(data)
    return fig_main_plot(data, ticker, buy_date, sell_date, int(sma_window), return_type), fig_indicators(data, max_prof)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
