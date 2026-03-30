import argparse
import sys
from app.agent import CommodityPredictionAgent
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the commodity price prediction agent.
    """
    parser = argparse.ArgumentParser(description="Predict prices for construction materials or commodities.")
    parser.add_argument("--material", type=str, default="gold", help="Material name (cement, pvc, land, steel, gold, etc.)")
    parser.add_argument("--nation", type=str, default="global", help="Nation for currency and local data (india, uk, europe, global)")
    
    args = parser.parse_args()

    # Predict commodity price
    agent = CommodityPredictionAgent(args.material, nation=args.nation)
    prediction_result = agent.run_prediction_pipeline()

    if prediction_result.get("success"):
        currency_symbol = "₹" if prediction_result['currency'] == "INR" else ("$" if prediction_result['currency'] == "USD" else ("£" if prediction_result['currency'] == "GBP" else "€"))
        print("\n" + "="*50)
        print(f"🏗️  Material: {prediction_result['material'].upper()} [{prediction_result['nation'].upper()}]")
        print(f"📊 Proxy Ticker: {prediction_result['symbol']}")
        print(f"💰 Predicted Price: {currency_symbol}{prediction_result['predicted_price']:,}")
        print(f"📰 Market Sentiment Score: {prediction_result['current_sentiment']}")
        print(f"⚠️  Model: {prediction_result['model_type']}")
        print("="*50 + "\n")
    else:
        logger.error(f"Prediction pipeline failed: {prediction_result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
