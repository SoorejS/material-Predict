import logging
from data.market_data import fetch_market_data
from data.news_data import fetch_news
from services.sentiment import analyze_sentiment
from features.feature_engineering import build_features
from models.train import train_baseline_model
from models.predict import predict_latest

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapping construction materials to relevant market tickers/proxies
MATERIAL_MAP = {
    "gold": "GC=F",
    "oil": "CL=F",
    "silver": "SI=F",
    "cement": "CX",               # Cemex (Global proxy for cement)
    "cement_india": "ULTRACEMCO.NS", # UltraTech Cement (India specific)
    "steel": "NUE",              # Nucor (Steel)
    "rebar": "SR=F",             # Steel Rebar Futures
    "pvc": "WLK",                # Westlake Corporation (PVC/Chemicals)
    "land": "VNQ",               # Vanguard Real Estate ETF (Proxy for land/property value)
    "lumber": "LBS=F",           # Lumber Futures
    "copper": "HG=F",            # Copper Futures
}

class CommodityPredictionAgent:
    """
    Orchestrates the entire commodity price prediction pipeline.
    """
    def __init__(self, material_name: str = "gold"):
        """
        Initializes the agent for a specific material or symbol.
        """
        self.material_name = material_name.lower()
        # Resolve to ticker or use as is
        self.symbol = MATERIAL_MAP.get(self.material_name, material_name.upper())

        # Determine news search query
        self.news_query = f"{self.material_name} price market news"
        if self.material_name == "cement":
            self.news_query = "cement manufacturing construction prices"
        elif self.material_name == "pvc":
            self.news_query = "PVC resin piping market news"
        elif self.material_name == "land":
            self.news_query = "real estate land residential price trends"

        logger.info(f"Initialized Prediction Agent for {self.material_name} (Ticker: {self.symbol}).")
        
    def run_prediction_pipeline(self) -> dict:
        """
        Runs the full pipeline from data fetching to prediction.
        :return: Dict containing results (prediction, sentiment, etc.)
        """
        try:
            # 1. Fetch historical market data (3 months)
            market_df = fetch_market_data(self.symbol, period="3mo")

            # 2. Fetch recent news and analyze sentiment using specialized query
            news = fetch_news(self.news_query)
            sentiment_score = analyze_sentiment(news)

            # 3. Build features (lag prices + news sentiment)
            processed_df = build_features(market_df.copy(), sentiment_score, lags=5)
            logger.info(f"Processed DF Shape: {processed_df.shape}")

            # 4. Train the baseline linear regression model
            model, feature_cols = train_baseline_model(processed_df)
            logger.info(f"Feature columns used for training: {feature_cols}")

            if model is None:
                raise ValueError("Model training failed.")

            # 5. Predict the next price for the commodity
            next_price = predict_latest(model, processed_df, feature_cols)

            # Compile results
            results = {
                "material": self.material_name,
                "symbol": self.symbol,
                "predicted_price": round(float(next_price), 2),
                "current_sentiment": round(float(sentiment_score), 2),
                "historical_data": market_df,  # Added for UI charts
                "model_type": "Linear Regression (Baseline)",
                "success": True
            }
            
            logger.info(f"Pipeline finished for {self.symbol}. Result: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed for {self.symbol}: {e}")
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test full agent
    agent = CommodityPredictionAgent("GC=F")
    result = agent.run_prediction_pipeline()
    print(result)
