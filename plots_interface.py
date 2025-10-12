from plotly.graph_objects import Scatter, Bar, Candlestick, Indicator, Figure
from plotly.subplots import make_subplots
from pandas import DataFrame, Timestamp, to_datetime
from calculations import count_price_runs, compute_sma, compute_daily_returns


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

    # Check for error result
    if max_profit.get('data_quality') == 'error':
        return graph_error_msg(max_profit.get('error_message', 'Unknown error occurred'), height=800)
    
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
        text="Best Buy Point",
        showarrow=True,
        arrowhead=2,
        ax=40,   # arrow offset on x-axis (0 = centered)
        ay=-40  # negative = arrow points upward
    )
    fig.add_annotation(
        x=max_profit["sell_date_single"],
        y=data["Close"].mean(),
        text="Best Sell Point",
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

    # Annotate buy/sell points for all transactions
    results = max_profit
    prices = data['Close'].tolist()
    dates = data['Date'].tolist()

    # Use all transactions without heavy filtering
    filtered_transactions = results['transactions'].copy()
    
    # Only filter out zero-profit transactions and ensure valid dates
    filtered_transactions = [t for t in filtered_transactions 
                           if t.get('profit', 0) > 0 and 
                           t['buy_day'] < len(dates) and 
                           t['sell_day'] < len(dates)]
    
    # Sort by buy date for chronological display
    filtered_transactions.sort(key=lambda x: x['buy_day'])
    
    # Limit number of transactions to avoid overcrowding
    max_transactions = 20
    if len(filtered_transactions) > max_transactions:
        filtered_transactions.sort(key=lambda x: x.get('return_percent', 0), reverse=True)
        filtered_transactions = filtered_transactions[:max_transactions]
        filtered_transactions.sort(key=lambda x: x['buy_day'])

    # Track ALL used positions for both annotations AND markers
    used_positions = {}  # key: (date, y_position), value: True
    
    def find_available_y_position(target_date, target_y, base_offset, price_range):
        """Find available Y position that doesn't overlap with existing elements"""
        offset_level = 0
        max_attempts = 10  # Prevent infinite loop
        
        while offset_level < max_attempts:
            # Calculate candidate Y position
            if offset_level % 2 == 0:  # Even levels: above
                candidate_y = target_y + base_offset * (offset_level // 2 + 1)
            else:  # Odd levels: below
                candidate_y = target_y - base_offset * (offset_level // 2 + 1)
            
            # Check if this position is available
            position_key = (target_date, candidate_y)
            if position_key not in used_positions:
                # Reserve this position
                used_positions[position_key] = True
                return candidate_y, offset_level
            
            offset_level += 1
        
        # If all positions taken, use the original (will overlap but rare)
        return target_y, -1

    # Calculate base offset based on price range
    price_range = max(prices) - min(prices)
    base_offset = price_range * 0.06  # Optimal spacing
    
    # Store marker positions separately for the scatter plot
    marker_buy_positions = []
    marker_sell_positions = []
    
    # First pass: Calculate all positions
    transaction_positions = []
    for i, transaction in enumerate(filtered_transactions):
        buy_date = dates[transaction['buy_day']]
        sell_date = dates[transaction['sell_day']]
        buy_price = prices[transaction['buy_day']]
        sell_price = prices[transaction['sell_day']]
        
        # Find available positions for buy annotation
        buy_annotation_y, buy_offset_level = find_available_y_position(
            buy_date, buy_price, base_offset, price_range
        )
        
        # Find available positions for sell annotation  
        sell_annotation_y, sell_offset_level = find_available_y_position(
            sell_date, sell_price, base_offset, price_range
        )
        
        # Store positions for markers (place markers at different Y than annotations)
        marker_buy_y, _ = find_available_y_position(buy_date, buy_price, base_offset * 0.3, price_range)
        marker_sell_y, _ = find_available_y_position(sell_date, sell_price, base_offset * 0.3, price_range)
        
        transaction_positions.append({
            'index': i,
            'buy_date': buy_date,
            'sell_date': sell_date,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'buy_annotation_y': buy_annotation_y,
            'sell_annotation_y': sell_annotation_y,
            'marker_buy_y': marker_buy_y,
            'marker_sell_y': marker_sell_y,
            'transaction': transaction
        })
        
        # Store marker positions for the scatter plot
        marker_buy_positions.append((buy_date, marker_buy_y))
        marker_sell_positions.append((sell_date, marker_sell_y))

    # Second pass: Create annotations and markers
    for pos in transaction_positions:
        i = pos['index']
        
        # Add buy annotation
        fig.add_annotation(
            x=pos['buy_date'], 
            y=pos['buy_annotation_y'],
            text=f"BUY{i+1}",
            showarrow=True, 
            arrowhead=2, 
            arrowsize=0.7,
            arrowcolor="crimson", 
            bgcolor="white", 
            bordercolor="crimson",
            font=dict(size=9, color="crimson"),
            yanchor="bottom" if pos['buy_annotation_y'] > pos['buy_price'] else "top"
        )
        
        # Add sell annotation
        fig.add_annotation(
            x=pos['sell_date'], 
            y=pos['sell_annotation_y'],
            text=f"SELL{i+1}",
            showarrow=True, 
            arrowhead=2, 
            arrowsize=0.7,
            arrowcolor="lime", 
            bgcolor="white", 
            bordercolor="lime", 
            font=dict(size=9, color="lime"),
            yanchor="bottom" if pos['sell_annotation_y'] > pos['sell_price'] else "top"
        )

    # Add ALL markers in a single scatter trace (more efficient)
    if marker_buy_positions and marker_sell_positions:
        # Separate buy and sell markers for different colors
        buy_dates, buy_ys = zip(*marker_buy_positions)
        sell_dates, sell_ys = zip(*marker_sell_positions)

        # Get the actual prices for hover text (not the offset marker positions)
        actual_buy_prices = [prices[transaction['buy_day']] for transaction in filtered_transactions]
        actual_sell_prices = [prices[transaction['sell_day']] for transaction in filtered_transactions]
        
        # Buy markers (red triangles down)
        fig.add_trace(Scatter(
            x=buy_dates,
            y=buy_ys,
            mode='markers',
            name='Buy Points',
            marker=dict(size=8, color='crimson', symbol='triangle-down'),
            hovertemplate='BUY: %{x}<br>Price: %{text:.2f}<extra></extra>',
            text=actual_buy_prices  # Show actual price, not offset position
        ))
        
        # Sell markers (green triangles up)
        fig.add_trace(Scatter(
            x=sell_dates,
            y=sell_ys,
            mode='markers',
            name='Sell Points', 
            marker=dict(size=8, color='lime', symbol='triangle-up'),
            hovertemplate='SELL: %{x}<br>Price: %{text:.2f}<extra></extra>',
            text=actual_sell_prices  # Show actual price, not offset position
        ))

    return fig


def fig_indicators(data:DataFrame, single_profit:float) -> Figure:
    """Creates an indicator graph showing multiple transaction profits"""
    from calculations import count_price_runs, max_profit
    
     # Check if received an error result (dict with data_quality='error')
    if isinstance(max_profit, dict) and max_profit.get('data_quality') == 'error':
        return graph_error_msg(max_profit.get('error_message', 'Unknown error occurred'))

    # Use max_profit function to get both single and multiple profits
    prices = data['Close'].tolist()
    dates = data['Date'].tolist()
    
    # Call max_profit to get the complete result with both profits
    profit_result = max_profit(prices, dates)
    
    # Use the single profit passed from main.py and get multiple profit from the result
    multiple_profit = profit_result['total_profit_multiple']
    
    # Get price runs for trend indicators
    price_runs = count_price_runs(data)

    fig = make_subplots(
        rows=4,  
        cols=2,
        specs=[
            [{"type": "domain"}, {"type": "domain"}], 
            [{"type": "domain"}, {"type": "domain"}],
            [{"type": "domain"}, {"type": "domain"}], 
            [{"type": "domain"}, {"type": "domain"}], 
            ]
        )

    # Single transaction max profit
    fig.add_trace(Indicator(
        mode = "number",
        value = single_profit,
        title = {"text": "Single Transaction Max Profit"},
        number={"font": {"color": "blue"}}), row=1, col=1)
    
    # Multiple transactions total profit
    fig.add_trace(Indicator(
        mode = "number",
        value = multiple_profit,
        title = {"text": "Multiple Transactions Total Profit"},
        number={"font": {"color": "green"}}), row=1, col=2)
    
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
        height=1000,   
        margin=dict(l=20, r=20, t=50, b=20)
        
    )
    
    return fig

def error_page(error_msg:str) -> Figure:
    empty_fig = Figure()         # Empty fig with error message
    empty_fig.add_annotation(
        text=error_msg,
        xref="paper", yref="paper",
        x=0.5, y=1, showarrow=False,    # Edited y to 1 for better visibility
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