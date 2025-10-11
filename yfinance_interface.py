from yfinance import download
from pandas import DataFrame

def get_stock_data(ticker:str, start_date:str, end_date:str) -> DataFrame:
    """Get historical stock data from yfinance library.

    Args:
        ticker (str): ticker of company to get historical stock data.
        start_date (str): Start date.
        end_date (str): end date.

    Returns:
        Dataframe: Returns that historical data in a pendas Dataframe
    """

    data = download(ticker, start_date, end_date, group_by=ticker, auto_adjust=False)[ticker]
    # DataFrame has a MultiIndex, 
    # .reset_index() can remove the levels to only a single column.
    data = data.reset_index()

    # Adds a ticker column to identify ticker. 
    # Used for future multi ticker/company searches
    data['ticker'] = ticker  
    return data
