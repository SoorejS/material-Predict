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

# Specialized Mapping: { Material: { Nation: Ticker } }
MATERIAL_DATABASE = {
    "gold": {"global": "GC=F", "india": "MCXGOLD.NS"},
    "oil": {"global": "CL=F"},
    "cement": {"global": "CX", "india": "ULTRACEMCO.NS", "uk": "CRH.L"},
    "steel": {"global": "NUE", "india": "TATASTEEL.NS"},
    "pvc": {"global": "WLK", "india": "SUPREMEIND.NS"},
    "land": {"global": "VNQ", "india": "DLF.NS"},
    "bitumen": {"global": "VMC"},
    "waterproofing": {"global": "CSL"},
    "insulation": {"global": "OC"},
    "glass": {"global": "TGLS"},
    "sealant": {"global": "RPM"},
    "copper": {"global": "HG=F", "india": "MCXCOPPER.NS"},
    "aluminum": {"global": "AA", "india": "NATIONALUM.NS"}
}

# Nation Configurations: { Nation: { Currency: Symbol, Ticker: ExchangeRateTicker } }
NATION_CONFIG = {
    "global": {"currency": "USD", "rate_ticker": None},
    "india": {"currency": "INR", "rate_ticker": "USDINR=X"},
    "uk": {"currency": "GBP", "rate_ticker": "USDGBP=X"},
    "europe": {"currency": "EUR", "rate_ticker": "USDEUR=X"}
}

class CommodityPredictionAgent:
    """
    Orchestrates the entire commodity price prediction pipeline.
    """
    def __init__(self, material_name: str = "gold", nation: str = "global"):
        """
        Initializes the agent for a specific material and nation.
        """
        self.material_name = material_name.lower()
        self.nation = nation.lower() if nation.lower() in NATION_CONFIG else "global"
        
        # 1. Resolve to best available ticker (Nation-specific -> Global)
        material_data = MATERIAL_DATABASE.get(self.material_name, {"global": material_name.upper()})
        self.symbol = material_data.get(self.nation, material_data.get("global"))

        # 2. Setup currency details
        self.currency = NATION_CONFIG[self.nation]["currency"]
        self.ex_ticker = NATION_CONFIG[self.nation]["rate_ticker"]

        # 3. Determine news search query (include nation for context)
        self.news_query = f"{self.material_name} price trends {self.nation if self.nation != 'global' else ''}"
        
        logger.info(f"Initialized Agent: {self.material_name} [{self.nation}] -> Ticker: {self.symbol} ({self.currency})")
        
    def run_prediction_pipeline(self) -> dict:
        """
        Runs the full pipeline from data fetching to prediction.
        :return: Dict containing results (prediction, sentiment, etc.)
        """
        try:
            # 1. Fetch historical market data (3 months)
            market_df = fetch_market_data(self.symbol, period="3mo")
            
            # 2. Handle Currency Conversion if necessary
            # Note: Tickers ending in .NS (NSE) or .L (London) are already in local currency.
            # Only convert if using a global (USD) proxy for a local nation.
            is_global_ticker = ".NS" not in self.symbol and ".L" not in self.symbol and self.symbol != "MCX"
            exchange_rate = 1.0

            if self.nation != "global" and is_global_ticker and self.ex_ticker:
                logger.info(f"Using global proxy for {self.nation}. Fetching exchange rate {self.ex_ticker}...")
                ex_df = fetch_market_data(self.ex_ticker, period="5d")
                exchange_rate = float(ex_df['Close'].iloc[-1])
                # Adjust historical prices to local currency
                market_df['Close'] = market_df['Close'] * exchange_rate
                logger.info(f"Prices adjusted by exchange rate: {exchange_rate:.2f}")

            # 3. Fetch recent news and analyze sentiment using specialized query
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
                "nation": self.nation,
                "currency": self.currency,
                "symbol": self.symbol,
                "predicted_price": round(float(next_price), 2),
                "current_sentiment": round(float(sentiment_score), 2),
                "historical_data": market_df,
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
