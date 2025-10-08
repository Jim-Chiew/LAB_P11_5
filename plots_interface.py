from plotly.graph_objects import Scatter, Bar, Candlestick, Figure, Indicator
from plotly.subplots import make_subplots
from calculations import count_price_runs, compute_sma, compute_daily_returns, max_profitv3

def fig_line_plot(data, ticker, buy_day, sell_day, sma_window):
    # Create only 3 graphs as originally intended
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.5, 0.2, 0.3],
                        vertical_spacing=0.05, 
                        subplot_titles=("SMA and closing price", "Daily returns", "Trends"))

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
    fig.add_trace(Bar(
        x=data["Date"],
        y=data["Daily_Return"],
        name="Daily Return",
        marker_color="tomato"
    ), row=2, col=1)

    # Candlestick (row 3)
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
        height=1500,
        width=1200  # ADD FIXED WIDTH FOR CONSISTENCY
    )

    return fig

def fig_profit_analysis(data, ticker):
    """Profit analysis graph showing ALL multiple transactions"""
    results = max_profitv3(data)
    prices = data['Close'].tolist()
    dates = data['Date'].tolist()
    
    fig = Figure()
    
    # Price line
    fig.add_trace(Scatter(
        x=data["Date"],
        y=data["Close"],
        mode='lines', 
        name='Price',
        line=dict(color='darkblue', width=2)
    ))
    
    # Single transaction markers (Best overall)
    fig.add_trace(Scatter(
        x=[dates[results['buy_day_single']], dates[results['sell_day_single']]], 
        y=[prices[results['buy_day_single']], prices[results['sell_day_single']]],
        mode='markers+text', 
        name='Single Transaction',
        marker=dict(size=14, color=['red', 'green'], symbol='diamond'),
        text=['BUY', 'SELL'], 
        textposition="top center"
    ))
    
    # Show ALL transactions without limiting
    for i, transaction in enumerate(results['transactions']):
        fig.add_trace(Scatter(
            x=[dates[transaction['buy_day']], dates[transaction['sell_day']]],
            y=[prices[transaction['buy_day']], prices[transaction['sell_day']]],
            mode='markers+text', 
            name='Multi Transaction' if i == 0 else '',
            marker=dict(size=6, color=['crimson', 'lime'], symbol=['triangle-down', 'triangle-up']),
            text=['BUY', 'SELL'], 
            textposition="top center",
            showlegend=(i == 0)
        ))
    
    profit_comparison = f"Single: ${results['max_profit_single']:.2f} | Multiple: ${results['total_profit_multiple']:.2f}"
    
    fig.update_layout(
        title=f"{ticker} - {profit_comparison}",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        showlegend=True,
        legend=dict(bgcolor="lightgrey"),
        height=600,
        width=1200,
        margin=dict(l=50, r=50, t=80, b=50)
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
        height=600,
        width=1200  # ADDED: Same width as other graphs
    )
    
    return fig

if __name__ == "__main__":
    pass