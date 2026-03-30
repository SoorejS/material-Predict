import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_market_data(symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical market data for a given symbol from Yahoo Finance.
    :param symbol: Symbol of the commodity (e.g., 'GC=F' for Gold)
    :param period: Data period (default '3mo')
    :param interval: Data interval (default '1d')
    :return: DataFrame with 'Date' and 'Close' prices
    """
    try:
        logger.info(f"Fetching {period} of market data for {symbol}...")
        df = yf.download(symbol, period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data found for symbol {symbol}")

        # Flatten MultiIndex columns if necessary (common in new yfinance versions)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Keep only the 'Close' price and reset index to have 'Date' as a column
        df = df[['Close']].copy()
        df.reset_index(inplace=True)
        
        logger.info(f"Successfully fetched {len(df)} data points for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise e

if __name__ == "__main__":
    # Test fetch
    data = fetch_market_data("GC=F")
    print(data.tail())
