from pandas import DataFrame
import numpy as np


def compute_sma(data:DataFrame, window:int=20):
    # data[f'SMA'] = data['Close'].rolling(window=window).mean()  # validation code
    window_sum = sum(data['Close'].iloc[:window])                 # sliding window to get SMA
    results = [window_sum / window]
    for i in range(window, len(data)):
        window_sum += data['Close'].iloc[i] - data['Close'].iloc[i - window]
        results.append(window_sum / window)
    data['SMA'] = [np.nan] * (window - 1) + results            # NAN for (n-1) data that is not computable
    return data


def compute_daily_returns(data:DataFrame, return_type:str='both'):
    """
    Calculate daily returns with multiple options
    
    Parameters:
    - return_type: 'log' for log returns, 'simple' for percentage returns
    """
    
    # Simple percentage returns
    if return_type in 'simple':
        data['Daily_Return'] = data['Close'].pct_change() * 100
    
    # Log returns
    # Calculate log returns using NumPy
    if return_type in 'log':
        # Use vectorized NumPy operations for better performance
        close_prices = data['Close'].values
        shifted_prices = data['Close'].shift(1).values
        
        # Calculate ratio and handle division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            ratio = np.divide(close_prices, shifted_prices)
            log_returns = np.log(ratio)
        
        # Replace inf/-inf with NaN (from division by zero or log(0))
        log_returns = np.where(np.isfinite(log_returns), log_returns, np.nan)
        
        data['Daily_Return'] = log_returns
    
    return data


def max_profit(data:DataFrame):
    min_price = max_profit = temp_buy_day = data.iloc[0]["Close"]
    buy_day = sell_day = temp_buy_day = data.iloc[0]["Date"]
    for _, row_data in data.iterrows():
        price = row_data["Close"]
        if  price < min_price:
            min_price = price
            temp_buy_day = row_data["Date"]
        
        if price - min_price > max_profit:
            max_profit = price - min_price
            buy_day = temp_buy_day
            sell_day = row_data["Date"]
    return max_profit, buy_day, sell_day


def max_profitv2(data:DataFrame):
    max_data = data.loc[data["Close"].idxmax()]
    min_data = data.loc[data["Close"].idxmin()]

    profit = max_data["Close"] - min_data["Close"]
    buy_date = min_data["Date"]
    sell_date = max_data["Date"]
    return profit, buy_date, sell_date


def max_profitv3(data:DataFrame):
    """Enhanced max profit with single and multiple transactions - AGGRESSIVE APPROACH"""
    prices = data['Close'].tolist()
    dates = data['Date'].tolist()
    
    # Single Transaction (buy once, sell once)
    min_price = float('inf')
    max_profit_single = 0
    buy_day_single = sell_day_single = 0
    temp_buy_day = 0
    
    for i, price in enumerate(prices):
        if price < min_price:
            min_price = price
            temp_buy_day = i
        
        profit = price - min_price
        if profit > max_profit_single:
            max_profit_single = profit
            buy_day_single = temp_buy_day
            sell_day_single = i
    
    # Multiple Transactions
    total_profit_multiple = 0
    transactions = []
    
    # Strategy 1: Buy at every local minimum, sell at next local maximum
    i = 0
    while i < len(prices) - 1:
        # Find local minimum (buy point)
        while i < len(prices) - 1 and prices[i] >= prices[i + 1]:
            i += 1
        
        if i >= len(prices) - 1:
            break
            
        buy_day = i
        buy_price = prices[i]
        
        # Find local maximum (sell point)  
        i += 1
        while i < len(prices) - 1 and prices[i] <= prices[i + 1]:
            i += 1
            
        sell_day = i
        sell_price = prices[i]
        
        profit = sell_price - buy_price
        
        if profit > 0:  # Only profitable trades
            total_profit_multiple += profit
            transactions.append({
                'buy_day': buy_day,
                'sell_day': sell_day,
                'buy_date': dates[buy_day],
                'sell_date': dates[sell_day],
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit': profit,
                'return_percent': (profit / buy_price) * 100
            })
        
        i += 1
    
    # If still no transactions, use the simple consecutive day approach as back up
    if len(transactions) < 10:  # If too few transactions
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                profit = prices[i] - prices[i-1]
                total_profit_multiple += profit
                transactions.append({
                    'buy_day': i-1,
                    'sell_day': i,
                    'buy_date': dates[i-1],
                    'sell_date': dates[i],
                    'buy_price': prices[i-1],
                    'sell_price': prices[i],
                    'profit': profit,
                    'return_percent': (profit / prices[i-1]) * 100
                })
    
    # Sort by date to see chronological distribution
    transactions.sort(key=lambda x: x['buy_day'])
    
    # print(f"Total transactions found: {len(transactions)}")
    # if transactions:
    #     print(f"First transaction: {transactions[0]['buy_date']}")
    #     print(f"Last transaction: {transactions[-1]['buy_date']}")
    
    return {
        'max_profit_single': max_profit_single,
        'buy_day_single': buy_day_single,
        'sell_day_single': sell_day_single,
        'buy_date_single': dates[buy_day_single],
        'sell_date_single': dates[sell_day_single],
        'buy_price_single': prices[buy_day_single],
        'sell_price_single': prices[sell_day_single],
        'total_profit_multiple': total_profit_multiple,
        'transactions': transactions,
        'average_profit_per_trade': total_profit_multiple / len(transactions) if transactions else 0,
        'num_transactions': len(transactions),
        'best_transaction': transactions[0] if transactions else None
    }


def count_price_runs(data:DataFrame):
    """
    1. Count: Number of consecutive upward or downward trends.
        A sequence of 1 or more days moving in the same direction (upward or downward) counts as 1 trend.
    2. Total_Days: Total number of days that were upward or downward, respectively.
    3. Highest: The longest streak of consecutive upward or downward days in a single trend.
    """
    runs = {'upward': {'count': 0, 'total_days': 0,'highest': 0},
            'downward': {'count': 0, 'total_days': 0, 'highest': 0}}
    current_run = {'type': None, 'length': 0}
    up_runs = []                                                    # store lengths of runs
    down_runs = []

    for i in range(1, len(data)):
        if data['Close'][i] > data['Close'][i-1]:                   # determine run type
            run_type = 'up'
        elif data['Close'][i] < data['Close'][i-1]:
            run_type = 'down'
        else:
            run_type = 'flat'

        if run_type == current_run['type']:                         # +1 if same run type
            current_run['length'] += 1
        else:
            if current_run['type'] == 'up':                         # store completed run
                up_runs.append(current_run['length'])               # compute runs in O(n)
            elif current_run['type'] == 'down':
                down_runs.append(current_run['length'])
            current_run = {'type': run_type, 'length': 1 if run_type != 'flat' else 0}

    # Append the last run if it was an up or down run
    if current_run['type'] == 'up':
        up_runs.append(current_run['length'])
    elif current_run['type'] == 'down':
        down_runs.append(current_run['length'])

    runs['upward']['count'] = len(up_runs)                          # summarize runs
    runs['upward']['total_days'] = sum(up_runs)                     # update dictionary in O(1)
    runs['downward']['count'] = len(down_runs)                      
    runs['downward']['total_days'] = sum(down_runs)
    runs['upward']['highest'] = max(up_runs) if up_runs else 0
    runs['downward']['highest'] = max(down_runs) if down_runs else 0

    return runs
