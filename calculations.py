import pandas as pd
import numpy as np  # Added import
from pandas import DataFrame, Timestamp
from numpy import nan, errstate, where, divide, log, isfinite

def compute_sma(data:DataFrame, window:int=20) -> DataFrame:
    # data[f'SMA'] = data['Close'].rolling(window=window).mean()  # validation code

    # Check if window is larger than available data
    if len(data) < window:
        # If not enough data, return all NaN or handle differently
        data['SMA'] = np.nan
        return data
    
    window_sum = sum(data['Close'].iloc[:window])                 # sliding window to get SMA
    results = [window_sum / window]
    for i in range(window, len(data)):
        window_sum += data['Close'].iloc[i] - data['Close'].iloc[i - window]
        results.append(window_sum / window)
    data['SMA'] = [nan] * (window - 1) + results            # NAN for (n-1) data that is not computable
    return data

def compute_daily_returns(data:DataFrame, return_type:str='both') -> DataFrame:
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
        with errstate(divide='ignore', invalid='ignore'):
            ratio = divide(close_prices, shifted_prices)
            log_returns = log(ratio)
        
        # Replace inf/-inf with NaN (from division by zero or log(0))
        log_returns = where(isfinite(log_returns), log_returns, nan)
        
        data['Daily_Return'] = log_returns
    
    return data

def max_profit_edge_case(data):   
    # Edge case handling: Validate input data before processing
    if data is None or data.empty or len(data) == 0:
        return create_empty_result("No data provided")
    
    # Check for required columns
    required_columns = ['Date', 'Close']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return create_empty_result(f"Missing required columns: {missing_columns}")
    
    # Check for minimum data points
    if len(data) < 2:
        return create_empty_result("Need at least 2 data points for analysis")
    
    # Check for valid data types and NaN values
    try:
        prices = data['Close'].tolist()
        dates = data['Date'].tolist()
        
        # Check for NaN or invalid values in prices
        if any(not isinstance(price, (int, float)) or pd.isna(price) for price in prices):
            return create_empty_result("Invalid price data contains NaN or non-numeric values")
            
    except (KeyError, TypeError, ValueError) as e:
        return create_empty_result(f"Data processing error: {str(e)}")
    
    # Check for edge case of all zero/negative prices
    if all(price <= 0 for price in prices):
        # Process anyway but flag as edge case
        result = max_profit(prices, dates)
        result['data_quality'] = 'edge_case'
        result['issue'] = "All prices are zero or negative"
        return result
    
    # If all validations pass, proceed with original logic
    return max_profit(prices, dates)

def max_profit(prices, dates):
    # Single Transaction (buy once, sell once)
    min_price = float('inf')
    max_profit_single = 0
    buy_day_single = sell_day_single = 0
    temp_buy_day = 0

    # Iterate through all prices to find optimal single transaction
    for i, price in enumerate(prices):
        # Update minimum price if current price is lower
        if price < min_price:
            min_price = price   # If new lowest price found
            temp_buy_day = i    # Update temp buy day
        
        profit = price - min_price
        if profit > max_profit_single:
            max_profit_single = profit
            buy_day_single = temp_buy_day
            sell_day_single = i
    
    # Multiple Transactions
    total_profit_multiple = 0
    transactions = []
    
    # Buy at every local minimum, sell at next local maximum
    i = 0
    n = len(prices)  # Store length for efficiency
    
    while i < n - 1:
        # Find local minimum (buy point)
        while i < n - 1 and prices[i] >= prices[i + 1]:
            i += 1 # Move forward while prices are decreasing
        
        # Exit if reach end of price list
        if i >= n - 1:
            break
            
        buy_day = i             # Found local minimum - buy day
        buy_price = prices[i]   # Buy price at local minimum
        
        # Find local maximum (sell point)  
        i += 1      # Move to next day after buying
        
        if i >= n:
            break
            
        while i < n - 1 and prices[i] <= prices[i + 1]:
            i += 1  # Move forward while prices are increasing
            
        sell_day = i            # Found local maximum - sell day
        
        if sell_day >= n:
            sell_day = n - 1
            
        sell_price = prices[sell_day]  # Sell price at local maximum
        
        profit = sell_price - buy_price
        
        if profit > 0:  # Only record profitable trades
            total_profit_multiple += profit
            transactions.append({
                'buy_day': buy_day,
                'sell_day': sell_day,
                'buy_date': dates[buy_day] if buy_day < len(dates) else None,
                'sell_date': dates[sell_day] if sell_day < len(dates) else None,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit': profit,
                'return_percent': (profit / buy_price) * 100 if buy_price > 0 else 0
            })
        
        i += 1  # Move to next day to look for new transaction
    
    # If still no transactions, use the simple consecutive day approach as back up
    if len(transactions) < 10:  # If too few transactions
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                profit = prices[i] - prices[i-1]     # Daily profit
                total_profit_multiple += profit      # Add to total
                transactions.append({                # Store transaction    
                    'buy_day': i-1,
                    'sell_day': i,
                    'buy_date': dates[i-1] if (i-1) < len(dates) else None,
                    'sell_date': dates[i] if i < len(dates) else None,
                    'buy_price': prices[i-1],
                    'sell_price': prices[i],
                    'profit': profit,
                    'return_percent': (profit / prices[i-1]) * 100 if prices[i-1] > 0 else 0
                })

    # Sort by date to see chronological distribution
    transactions.sort(key=lambda x: x['buy_day'])
    
    result = {
        'max_profit_single': max_profit_single,
        'buy_day_single': buy_day_single,
        'sell_day_single': sell_day_single,
        'total_profit_multiple': total_profit_multiple,
        'transactions': transactions,
        'num_transactions': len(transactions),
        'average_profit_per_trade': total_profit_multiple / len(transactions) if transactions else 0,
        'data_quality': 'normal'
    }
    
    if buy_day_single < len(dates):
        result['buy_date_single'] = dates[buy_day_single]
    else:
        result['buy_date_single'] = None
        
    if sell_day_single < len(dates):
        result['sell_date_single'] = dates[sell_day_single]
    else:
        result['sell_date_single'] = None
        
    if buy_day_single < len(prices):
        result['buy_price_single'] = prices[buy_day_single]
    else:
        result['buy_price_single'] = 0
        
    if sell_day_single < len(prices):
        result['sell_price_single'] = prices[sell_day_single]
    else:
        result['sell_price_single'] = 0
        
    result['best_transaction'] = max(transactions, key=lambda x: x['profit']) if transactions else None
    
    return result

def create_empty_result(error_message):
    """Return consistent empty result for error cases"""
    
    return {
        'max_profit_single': 0,
        'buy_day_single': 0,
        'sell_day_single': 0,
        'buy_date_single': None,
        'sell_date_single': None,
        'buy_price_single': 0,
        'sell_price_single': 0,
        'total_profit_multiple': 0,
        'transactions': [],
        'num_transactions': 0,
        'average_profit_per_trade': 0,
        'best_transaction': None,
        'data_quality': 'error',
        'error_message': error_message 
    }

def count_price_runs(data:DataFrame) -> dict:
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
            if current_run['type'] == 'up':
                if current_run['length'] >= 2:                         # store completed run
                    up_runs.append(current_run['length'])
            elif current_run['type'] == 'down':
                if current_run['length'] >= 2:
                    down_runs.append(current_run['length'])
            current_run = {'type': run_type, 'length': 1 if run_type != 'flat' else 0}

    # Append the last run if it was an up or down run
    if current_run['length'] >= 2:
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
