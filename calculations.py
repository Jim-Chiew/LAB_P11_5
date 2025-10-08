
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



# def compute_daily_returns(data:DataFrame):
#     # data['Daily_Return'] = data['Close'].pct_change() * 100
#     data['Daily_Return'] = np.log(data['Close'] / data['Close'].shift(1))
#     return data

def compute_daily_returns(data:DataFrame, return_type='both'):
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
        
        data['Log_Daily_Return'] = log_returns
    
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
    prices = data['Close'].tolist()
    
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
    
    # Multiple Transactions (Record all profits)
    total_profit_multiple = 0
    transactions = []

    # Peak-Valley approach
    i = 0
    n = len(prices)
    
    while i < n - 1:
        # Find valley (wait for price to stop decreasing)
        while i < n - 1 and prices[i] >= prices[i + 1]:
            i += 1
        
        if i >= n - 1:
            break
            
        buy_day = i
        
        # Find peak (wait for price to stop increasing)
        i += 1
        while i < n - 1 and prices[i] <= prices[i + 1]:
            i += 1
            
        sell_day = i
        profit = prices[sell_day] - prices[buy_day]
        
        # Only record profitable transactions
        if profit > 0:
            total_profit_multiple += profit
            transactions.append({
                'buy_day': buy_day,
                'sell_day': sell_day,
                'profit': profit
            })
        i += 1
    return max_profit_single, transactions, buy_day_single, sell_day_single, total_profit_multiple


def count_price_runs(data:DataFrame):
    runs = {'upward': {'count': 0, 'total_days': 0},
            'downward': {'count': 0, 'total_days': 0}}
    
    direction = None
    length = 0
    
    for i in range(1, len(data)):
        if data['Close'].iloc[i] > data['Close'].iloc[i - 1]:
            if direction != 'up':
                if direction == 'down' and length > 1:
                    runs['downward']['count'] += 1
                    runs['downward']['total_days'] += length
                direction = 'up'
                length = 1
            else:
                length += 1
        elif data['Close'].iloc[i] < data['Close'].iloc[i - 1]:
            if direction != 'down':
                if direction == 'up' and length > 1:
                    runs['upward']['count'] += 1
                    runs['upward']['total_days'] += length
                direction = 'down'
                length = 1
            else:
                length += 1
        else:
            if direction in ['up', 'down'] and length > 1:
                runs[f'{direction}ward']['count'] += 1
                runs[f'{direction}ward']['total_days'] += length
            direction = None
            length = 0
    
    return runs
