from plotly.graph_objects import Scatter, Bar, Candlestick, Indicator, Figure
from plotly.subplots import make_subplots
from pandas import DataFrame, Timestamp, to_datetime
from calculations import count_price_runs, compute_sma, compute_daily_returns, max_profit_multiple


def fig_main_plot(data:DataFrame, ticker:str, max_profit:dict, sma_window:int, return_type:str="simple") -> Figure:
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

    data = compute_sma(data, sma_window)
    data = compute_daily_returns(data, return_type)

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
    fig.add_vline(x=max_profit["buy_date_single"], line_width=3, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_vline(x=max_profit["sell_date_single"], line_width=3, line_dash="dash", line_color="green", row=1, col=1)
    fig.add_annotation(
        x=max_profit["buy_date_single"],
        y=data["Close"].mean(),
        text="Best Buy",
        showarrow=True,
        arrowhead=2,
        ax=40,   # arrow offset on x-axis (0 = centered)
        ay=-40  # negative = arrow points upward
    )
    fig.add_annotation(
        x=max_profit["sell_date_single"],
        y=data["Close"].mean(),
        text="Best sell",
        showarrow=True,
        arrowhead=2,
        ax=60,   # arrow offset on x-axis (0 = centered)
        ay=60  # negative = arrow points upward
    )

    # Plot for daily return in bar plot. Row 2.
    colors = ['green' if x >= 0 else 'red' for x in data['Daily_Return']]
    fig.add_trace(Bar(
        x=data["Date"],
        y=data["Daily_Return"],
        name= return_type.capitalize() + " Daily Return",
        marker_color=colors
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

    prices = data['Close'].tolist()
    dates = data['Date'].tolist()
    filtered_transactions = max_profit_multiple(max_profit, dates)
    
    # Multiple transactions with dynamic positioning
    for i, transaction in enumerate(filtered_transactions):
        buy_date = dates[transaction['buy_day']]
        sell_date = dates[transaction['sell_day']]
        buy_price = prices[transaction['buy_day']]
        sell_price = prices[transaction['sell_day']]
        
        # Calculate dynamic offsets based on local density
        price_range = max(prices) - min(prices)
        base_offset = price_range * 0.04
        
        # Check for existing annotations at these dates
        buy_offsets_used = []
        sell_offsets_used = []
        # # Track used positions to avoid overlaps
        used_positions = {}
        single_buy_date = max_profit["buy_date_single"]
        single_sell_date = max_profit["sell_date_single"]
        # # Store single transaction positions
        used_positions[single_buy_date] = 'top'
        used_positions[single_sell_date] = 'top'
        
        # # for used_date, used_offset in used_positions.items():
        # #     if used_date == buy_date:
        # #         buy_offsets_used.append(used_offset)
        # #     if used_date == sell_date:
        # #         sell_offsets_used.append(used_offset)

        if buy_date not in used_positions:
            used_positions[buy_date] = []
        if sell_date not in used_positions:
            used_positions[sell_date] = []
        
        # Choose offsets that don't conflict
        available_offsets = [base_offset, -base_offset, base_offset*1.5, -base_offset*1.5, base_offset*2, -base_offset*2]
        
        buy_offset = next((off for off in available_offsets if off not in buy_offsets_used), base_offset)
        sell_offset = next((off for off in available_offsets if off not in sell_offsets_used), -base_offset)
        
        # Add text annotations with dynamic positioning
        fig.add_annotation(
            x=buy_date, y=buy_price + buy_offset,
            text=f"BUY{i+1}",  # Number the transactions
            showarrow=True, 
            arrowhead=2, 
            arrowsize=0.7,
            arrowcolor="crimson", 
            bgcolor="white", 
            bordercolor="crimson",
            font=dict(size=10, color="crimson")
        )
        
        fig.add_annotation(
            x=sell_date, y=sell_price + sell_offset,
            text=f"SELL{i+1}",  # Number the transactions
            showarrow=True, 
            arrowhead=2, 
            arrowsize=0.7,
            arrowcolor="lime", 
            bgcolor="white", 
            bordercolor="lime", 
            font=dict(size=10, color="lime")
        )
        
        # Update used positions
        used_positions[buy_date].append(buy_offset)
        used_positions[sell_date].append(sell_offset)
        

        # Add markers without text
        fig.add_trace(Scatter(
            x=[buy_date],
            y=[buy_price],
            mode='markers',
            name='Multi Transaction' if i == 0 else '',
            marker=dict(size=8, color=['crimson'], symbol=['triangle-down']),
            showlegend=(i == 0),
            hovertemplate=f'BUY {i+1}<br>Date: %{{x}}<br>Price: %{{y:.2f}}<extra></extra>'
        ))

        # Add markers without text
        fig.add_trace(Scatter(
            x=[sell_date],
            y=[sell_price],
            mode='markers',
            name='Multi Transaction' if i == 0 else '',
            marker=dict(size=8, color=['lime'], symbol=['triangle-up']),
            showlegend=(i == 0),
            hovertemplate=f'SELL {i+1}<br>Date: %{{x}}<br>Price: %{{y:.2f}}<extra></extra>'
        ))

    return fig


def fig_indicators(data:DataFrame, max_profit:float) -> Figure:
    """Creates an indicator graph. Numbers only. 

    Args:
        data (DataFrame): Contains stock historical data
        max_profit (float): Max profit value

    Returns:
        Figure (Figure): Returns a plotly figure object.
    """
    fig = make_subplots(
        rows=4, 
        cols=2,
        specs=[
            [{"type": "domain", "colspan": 2}, None], 
            [{"type": "domain"}, {"type": "domain"}], 
            [{"type": "domain"}, {"type": "domain"}], 
            [{"type": "domain"}, {"type": "domain"}],
            ]
        )

    price_runs = count_price_runs(data)
    fig.add_trace(Indicator(
        mode = "number",
        value = max_profit,
        title = {"text": "Max Profit Amount based on best buy/sell date"},
        number={"font": {"color": "green"}}), row=1, col=1)
    
    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['upward']['count'],
        title = {"text": "Number of upward trends"},
        number={"font": {"color": "green"}}), row=2, col=2)

    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['upward']['total_days'],
        title = {"text": "Total upward days in trends"},
        number={"font": {"color": "green"}},), row=3, col=2)
        
    fig.add_trace(Indicator(
            mode = "number",
            value = price_runs['upward']['highest'],
            title = {"text": "Highest number of upward day in a single trend"},
            number={"font": {"color": "green"}}), row=4, col=2)

    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['downward']['count'],
        title = {"text": "Number of downward trends"},
        number={"font": {"color": "red"}}), row=2, col=1)

    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['downward']['total_days'],
        title = {"text": "Total downward days in trends"},
        number={"font": {"color": "red"}}), row=3, col=1)

    fig.add_trace(Indicator(
        mode = "number",
        value = price_runs['downward']['highest'],
        title = {"text": "Highest number of downward day in a single trend"},
        number={"font": {"color": "red"}}), row=4, col=1)
    
    fig.update_layout(
    height=600
    )
    
    return fig

def error_page(error_msg:str) -> Figure:
    empty_fig = Figure()         # Empty fig with error message
    empty_fig.add_annotation(
        text=error_msg,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="red"),
        align="center"
    )
    empty_fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return empty_fig

def graph_error_msg(error_message: str, height: int = 400) -> Figure:
    """Create a standardized error figure with the error message"""
    error_fig = Figure()
    
    error_fig.add_annotation(
        text=f"❌ ANALYSIS ERROR<br>{error_message}",
        xref="paper", yref="paper",
        x=0.5, y=1, showarrow=False,
        font=dict(size=16, color="red"),
        align="center",
        bgcolor="lightyellow",
        bordercolor="red",
        borderwidth=2
    )
    
    error_fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        height=height
    )
    return error_fig