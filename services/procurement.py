"""
CCIE Elite Procurement Advisor Node
Calculates optimal buying strategy (Buy/Wait) and estimated savings.
"""

class ProcurementAdvisor:
    """
    Analyzes current and future prices to generate actionable advice.
    """
    def __init__(self, current_price: float, future_price: float, qty: float):
        self.p_now = current_price
        self.p_future = future_price
        self.qty = qty
        
    def generate_strategy(self, material_name: str) -> dict:
        """
        Input: Prices and Material units.
        Output: Strategy (BUY_NOW, WAIT, HOLD) and savings.
        """
        diff_pct = (self.p_future - self.p_now) / self.p_now
        savings = (self.p_future - self.p_now) * self.qty
        
        status = "HOLD ⚪"
        recommendation = "Standard regular purchasing."
        
        if diff_pct > 0.05:
            status = "BUY_NOW 🔥"
            recommendation = f"Immediate purchase advised. Predicted {diff_pct*100:.1f}% price hike in next phase."
        elif diff_pct < -0.05:
            status = "WAIT 🕒"
            recommendation = f"Purchase deferral advised. Predicted {abs(diff_pct)*100:.1f}% price drop in next phase."
        else:
            status = "HOLD ⚖️"
            recommendation = f"Market volatility low. Purchase as per timeline."
            
        return {
          "material": material_name,
          "strategy": status,
          "recommendation": recommendation,
          "est_savings": round(savings, 2)
        }

if __name__ == "__main__":
    pa = ProcurementAdvisor(400, 450, 500)
    print(pa.generate_strategy("Cement"))
