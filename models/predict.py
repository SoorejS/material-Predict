import pandas as pd
import logging
from sklearn.linear_model import LinearRegression

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def predict_latest(model: LinearRegression, df: pd.DataFrame, feature_cols: list) -> float:
    """
    Predicts the next closing price based on the latest available features.
    :param model: Trained LinearRegression model
    :param df: Processed DataFrame with latest values
    :param feature_cols: Names of the feature columns
    :return: Predicted next closing price
    """
    try:
        # Get the latest row of features (the most recent available data)
        latest_features = df[feature_cols].tail(1)
        
        # Prediction
        prediction = model.predict(latest_features)[0]
        
        logger.info(f"Latest prediction: {prediction:.2f}")
        return prediction
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return -1.0

if __name__ == "__main__":
    # Test prediction
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    # Dummy data
    X = [[100, 0.5], [101, 0.6]]
    y = [102, 103]
    model.fit(X, y)
    df = pd.DataFrame({'lag_1': [101], 'sentiment': [0.6]})
    print(f"Predicted price: {predict_latest(model, df, ['lag_1', 'sentiment'])}")
