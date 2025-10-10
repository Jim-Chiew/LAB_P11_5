def compute_sma(data, window=20):
    data[f'SMA'] = data['Close'].rolling(window=window).mean()
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
        print("Using fallback consecutive day approach...")
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

def count_price_runs(data):
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
