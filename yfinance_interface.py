from yfinance import download

def get_stock_data(ticker, start_date, end_date):
    #start_date = '1990-01-01'
    #end_date = '2024-08-1'

    # Set the ticker
    #ticker = 'AMZN'
    data = download(ticker, start_date, end_date, group_by=ticker, auto_adjust=False)[ticker]
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html
    data = data.reset_index()  # DataFrame has a MultiIndex, this method can remove the levels to only a single column.
    data['ticker'] = ticker
    return data
