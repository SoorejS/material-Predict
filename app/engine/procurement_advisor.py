import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcurementAdvisor:
    """
    Analyzes price drifts across construction phases and recommends a buying strategy.
    Input: Current prices, Predicted drifts, and Phase-wise material requirements.
    Output: Actionable procurement advice with estimated savings.
    """
    def __init__(self):
        pass

    def analyze_procurement(self, current_price: float, drift_pct: float, phase_qty: float) -> dict:
        """
        Calculates if buying now (Month 1) saves more than buying in the phase of use.
        """
        # Forecasted price at phase-of-use (Month 3)
        future_price = current_price * (1 + drift_pct)**2
        
        # Savings by buying now (ignoring storage costs for this high-level logic)
        savings = (future_price - current_price) * phase_qty
        
        recommendation = "Hold Buying"
        buy_signal = "Low ⚪"
        
        if drift_pct > 0.03:  # If drift is > 3% per month
            recommendation = "Buy Now & Stockpile"
            buy_signal = "High 🔥"
        elif drift_pct > 0:
            recommendation = "Steady Purchase"
            buy_signal = "Medium 🟡"
            
        return {
            "recommendation": recommendation,
            "buy_signal": buy_signal,
            "potential_savings": round(savings, 2)
        }

if __name__ == "__main__":
    advisor = ProcurementAdvisor()
    # If steel is 75/kg now and drifting up 5%/mo
    print(advisor.analyze_procurement(75, 0.05, 5000))
