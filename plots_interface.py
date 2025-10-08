from plotly.graph_objects import Scatter, Bar, Candlestick, Figure, Indicator
from plotly.subplots import make_subplots
from calculations import count_price_runs, compute_sma, compute_daily_returns

def fig_line_plot(data, ticker, buy_day, sell_day, sma_window):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.5, 0.2, 0.3],  # top bigger than bottom
                        vertical_spacing=0.05, subplot_titles=("SMA and closing price", "Daily returns", "Trands"))

    data = compute_sma(data, sma_window)
    data = compute_daily_returns(data)

    # SMA
    fig.add_trace(Scatter(
        x=data["Date"],
        y=data["SMA"],
        mode="markers",
        line=dict(color="blue", width=2),
        marker=dict(size=4, color="purple"),
        name="SMA",
    ), row=1, col=1)

    # Closing
    fig.add_trace(Scatter(
        x=data["Date"],
        y=data["Close"],
        mode="lines",
        line=dict(color="blue", width=2),
        marker=dict(size=8, color="blue"),
        name="Close"
    ), row=1, col=1)

    # Daily return
    colors = ['green' if x >= 0 else 'red' for x in data['Daily_Return']]
    fig.add_trace(Bar(
        x=data["Date"],
        y=data["Daily_Return"],
        name="Daily Return",
        marker_color=colors,
    ), row=2, col=1)

    # Candlestick (row 1)
    fig.add_trace(Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Candlestick"
    ), row=3, col=1)

    fig.add_vline(x=buy_day, line_width=3, line_dash="dash", line_color="green", row=1, col=1)
    fig.add_vline(x=sell_day, line_width=3, line_dash="dash", line_color="red", row=1, col=1)

    fig.update_layout(
    title=ticker + " Stock Information:",
    xaxis_rangeslider_visible=False,
    margin=dict(l=20, r=15, t=50, b=0),
    height=1500
    )

    return fig

def fig_indicators(data, max_profit):
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
    #data = get_stock_data('AMZN', '1990-01-01', '2024-08-1')
    #max_prof, buy_day, sell_day = max_profitv2(data)
    #fig_indicators(data, max_prof).show()
    #fig_line_plot(data, 'AMZN', buy_day, sell_day).show()
    pass