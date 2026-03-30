"""
CCIE Elite Uncertainty Engine
Calculates cost range and confidence interval (±%) for bill of quantities.
"""

import random

class UncertaintyEngine:
    """
    Simulates prediction error and market volatility impact.
    """
    def __init__(self, baseline_cost: float, sentiment_score: float):
        self.baseline = baseline_cost
        self.sentiment = sentiment_score
        
    def calculate_range(self, error_pct: float = 0.08) -> dict:
        """
        Uses model error and sentiment volatility to generate project range.
        Input: Baseline cost and baseline model error (default 8%).
        Output: Min/Max cost and confidence percent.
        """
        # Sentiment-adjusted volatility: If sentiment is near 0, volatility is higher
        volatility = abs(self.sentiment) * 0.05 + error_pct
        
        # Uncertainty Interval Calculation
        cost_min = self.baseline * (1 - volatility)
        cost_max = self.baseline * (1 + volatility)
        
        # Confidence Level Calculation (Probability density simulation)
        # Higher sentiment = usually more news/data = higher confidence
        confidence = 100 - (volatility * 100)
        
        return {
          "cost_min": round(cost_min, 2),
          "cost_max": round(cost_max, 2),
          "confidence_pct": round(confidence, 1),
          "variance": round(volatility * 100, 1)
        }

if __name__ == "__main__":
    ue = UncertaintyEngine(1200000, 0.4)
    print(ue.calculate_range(0.08))
