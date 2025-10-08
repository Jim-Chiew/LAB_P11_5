import numpy


def compute_sma(data, window=20):
    # data[f'SMA'] = data['Close'].rolling(window=window).mean()  # validation code
    window_sum = sum(data['Close'].iloc[:window])                 # sliding window to get SMA
    results = [window_sum / window]
    for i in range(window, len(data)):
        window_sum += data['Close'].iloc[i] - data['Close'].iloc[i - window]
        results.append(window_sum / window)
    data['SMA'] = [numpy.nan] * (window - 1) + results            # NAN for (n-1) data that is not computable
    return data

def compute_daily_returns(data):
    data['Daily_Return'] = data['Close'].pct_change() * 100
    return data

def max_profit(data):
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

def max_profitv2(data):
    max_data = data.loc[data["Close"].idxmax()]
    min_data = data.loc[data["Close"].idxmin()]

    profit = max_data["Close"] - min_data["Close"]
    buy_date = min_data["Date"]
    sell_date = max_data["Date"]
    return profit, buy_date, sell_date

def max_profitv3(data):
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

def count_price_runs(data):
    runs = {'upward': {'count': 0, 'total_days': 0,'highest': 0},
            'downward': {'count': 0, 'total_days': 0, 'highest': 0}}
    current_run = {'type': None, 'length': 0}
    up_runs = []
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