from plotly.graph_objects import Scatter, Bar, Candlestick, Figure, Indicator
from plotly.subplots import make_subplots
from pandas import DataFrame, Timestamp
from calculations import count_price_runs, compute_sma, compute_daily_returns


def fig_main_plot(data:DataFrame, ticker:str, buy_day:Timestamp, sell_day:Timestamp, sma_window:int, return_type: str='simple'):
    """Generates main graph that contains 3 types of sub plots.
        1. Scatter plot that contains SMA, Close price and best day to buy/sell.
        2. Bar plot that shows daily returns.
        3. Candlestick plot that shows stock trends.

    Args:
        data (DataFrame): Contains stock historical data
        ticker (str): Ticker of the company you want to view the stock trend of 
        buy_day (Timestamp): Best day to buy the stock.
        sell_day (Timestamp): Best day to sell the stock
        sma_window (int): Defines number of days for SMA calculation.

    Returns:
        Figure (Figure): Returns a plotly figure object.
    """
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        # Defines how big each section is. total 1. 
                        # Exp: [0.5, 0.5] will have 2 row with equal space
                        row_heights=[0.5, 0.2, 0.3],
                        vertical_spacing=0.05, 
                        subplot_titles=("SMA and closing price", "Daily returns", "Trends")
                        )
    
    # DEBUG: Check what we have
    # print(f"DEBUG: return_type = {return_type}")
    # print(f"DEBUG: Columns before compute_daily_returns: {data.columns.tolist()}")

    data = compute_sma(data, sma_window)
    data = compute_daily_returns(data, return_type)

    # print(f"DEBUG: Columns after compute_daily_returns: {data.columns.tolist()}")

    # Plot for SMA in scatter plot. Row 1. 
    fig.add_trace(Scatter(
        x=data["Date"],
        y=data["SMA"],
        mode="markers",
        line=dict(color="blue", width=2),
        marker=dict(size=4, color="purple"),
        name="SMA",
    ), row=1, col=1)

    # Plot for close date in scatter plot. Row 1.
    fig.add_trace(Scatter(
        x=data["Date"],
        y=data["Close"],
        mode="lines",
        line=dict(color="blue", width=2),
        marker=dict(size=8, color="blue"),
        name="Close"
    ), row=1, col=1)

    # virtical line to indicate Buy/sell dates. in scatter plot. Row 1.  
    fig.add_vline(x=buy_day, line_width=3, line_dash="dash", line_color="green", row=1, col=1)
    fig.add_vline(x=sell_day, line_width=3, line_dash="dash", line_color="red", row=1, col=1)

    # Plot for daily return in bar plot. Row 2.
    if return_type == 'log':
        returns_col = 'Log_Daily_Return'

        '''
        I multiplied by 100 because it is for better visuality. Raw logs returns are very small, typically between -0.1 to 0.1 only, which 
        is very hard for it to be reflected in the graph. Multiply log returns by 100 to make them more visible (convert to percentage-like)
        '''
        name = "Log Daily Return (×100)"
        y_data = data[returns_col] * 100
        colors = ['black' for x in data[returns_col]]

    else:
        returns_col = 'Daily_Return'
        name = "Daily Return (%)"
        colors = ['green' if x >= 0 else 'red' for x in data[returns_col]]
        
    fig.add_trace(Bar(
        x=data["Date"],
        y=data[returns_col],
        name=name,
        marker_color=colors,
        opacity=0.7
    ), row=2, col=1)

    # Plot for stock trand in Candlestick plot. Row 3.
    fig.add_trace(Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Candlestick"
    ), row=3, col=1)

    fig.update_layout(
    title=ticker + " Stock Information:",
    xaxis_rangeslider_visible=False,
    # Modify graph margin to remove/minimize empty spaces of the window.  
    margin=dict(l=20, r=15, t=50, b=0),
    height=1500
    )

    return fig


def fig_indicators(data:DataFrame, max_profit:float, return_type:str='simple'):
    """Creates an indicator graph. Numbers only. 

    Args:
        data (DataFrame): Contains stock historical data
        max_profit (float): Max profit value

    Returns:
        Figure (Figure): Returns a plotly figure object.
    """

    fig = Figure()

    price_runs = count_price_runs(data)
    fig.add_trace(Indicator(
        mode = "number",
        value = max_profit,
        title = {"text": "Max Profit Amount"},
        number={"font": {"color": "green"}},
        domain = {'x': [0, 1], 'y': [0.67, 1]}))
    
    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['upward']['count'],
        title = {"text": "Upward occurances"},
        number={"font": {"color": "green"}},
        domain = {'x': [0, 0.5], 'y': [0.33, 0.67]}))

    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['upward']['total_days'],
        title = {"text": "Upward total days"},
        number={"font": {"color": "green"}},
        domain = {'x': [0.5, 1], 'y': [0.33, 0.67]}))

    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['downward']['count'],
        title = {"text": "Downward occurances"},
        number={"font": {"color": "red"}},
        domain = {'x': [0, 0.5], 'y': [0, 0.33]}))

    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['downward']['total_days'],
        title = {"text": "Downward total days"},
        number={"font": {"color": "red"}},
        domain = {'x': [0.5, 1], 'y': [0, 0.33]}))
    
    fig.update_layout(
    height=600
    )
    
    return fig


if __name__ == "__main__":
    pass