import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_features(df: pd.DataFrame, sentiment: float, lags: int = 5) -> pd.DataFrame:
    """
    Creates feature columns for price prediction.
    :param df: DataFrame with 'Date' and 'Close' prices
    :param sentiment: Aggregate news sentiment score for the commodity
    :param lags: Number of daily price lags to include as features (default 5)
    :return: Processed DataFrame with price lags and sentiment features
    """
    try:
        # Create lag features (past days' prices)
        for i in range(1, lags + 1):
            df[f"lag_{i}"] = df["Close"].shift(i)

        # Include news sentiment as a constant feature for the whole period (or dynamic)
        df["sentiment"] = sentiment
        
        # Scaling sentiment based on historical mean can be added later
        # df["sentiment"] = df["sentiment"] * df["lag_1"].mean()  # Simple scaling
        
        # Drop rows with NaN values (from shifting)
        df = df.dropna().copy()
        
        logger.info(f"Built {len(df.columns) - 2} features for {len(df)} data points.")
        return df
    except Exception as e:
        logger.error(f"Error building features: {e}")
        return df

if __name__ == "__main__":
    # Test feature building
    data = pd.DataFrame({'Date': pd.date_range('2024-01-01', periods=10), 'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]})
    sentiment = 0.5
    print(build_features(data, sentiment).head())
