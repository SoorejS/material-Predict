from app.agent import CommodityPredictionAgent
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def material_prediction_tool(material_name: str) -> str:
    """
    Antigravity Tool: Predicts the next price for a given construction material or commodity.
    :param material_name: Name ('cement', 'pvc', 'land', 'steel', 'gold', etc.)
    :return: Formatted string with prediction and market sentiment
    """
    agent = CommodityPredictionAgent(material_name)
    result = agent.run_prediction_pipeline()

    if result.get("success"):
        return f"""
        🏗️  Material: {result['material'].upper()}
        📊 Proxy Ticker: {result['symbol']}
        💰 Predicted Price: {result['predicted_price']}
        📰 Market Sentiment: {result['current_sentiment']}
        ⚠️  Model: {result['model_type']}
        """
    else:
        return f"Error: {result.get('error')}"

if __name__ == "__main__":
    # Test tool wrapper
    print(commodity_prediction_tool("GC=F"))
