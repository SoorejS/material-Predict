from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_baseline_model(df: pd.DataFrame) -> (LinearRegression, list):
    """
    Trains a baseline linear regression model on the processed dataset.
    :param df: Cleaned DataFrame with lags and sentiment features
    :return: (Trained model, Name of model input features)
    """
    try:
        # Define features (X) and target (y)
        # Assuming df has 'Close', 'Date', and all others are features
        feature_cols = [col for col in df.columns if col not in ["Close", "Date"]]
        X = df[feature_cols]
        y = df["Close"].values.ravel()  # Use ravel to ensure 1D array

        # Instantiate linear regression
        model = LinearRegression()
        model.fit(X, y)

        # Baseline evaluation
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        
        logger.info(f"Model trained. Mean Squared Error: {mse:.4f}")
        return model, feature_cols
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return None, []

if __name__ == "__main__":
    # Test training
    data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10),
        'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'lag_1': [0, 100, 101, 102, 103, 104, 105, 106, 107, 108],
        'sentiment': [0.5]*10
    })
    model, cols = train_baseline_model(data)
    print(model, cols)
