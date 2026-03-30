import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskIntelligenceEngine:
    """
    Simulates Project Risk scoring and Cost Benchmarking for your project.
    """
    def __init__(self, nation: str):
        self.nation = nation.lower()
        # Market Benchmark Costs (e.g., standard price per built-up sqft)
        self.benchmarks = {
            "india": 1800,  # ₹1,800/sqft
            "uk": 250,      # £250/sqft
            "global": 150,  # $150/sqft
            "europe": 200   # €200/sqft
        }
        
    def score_risk(self, soil_type: str, floors: int, price_drift: float) -> dict:
        """
        Calculates a Risk Score based on geometry and market volatility.
        """
        score = 0
        if soil_type.lower() == "soft": score += 30
        if floors > 2: score += 20
        if price_drift > 0.05: score += 40
        
        # Risk Categories: Low (0-40), Medium (41-70), High (71+)
        category = "Low 🟢"
        if score > 70: category = "High 🔴"
        elif score > 40: category = "Medium 🟡"
        
        return {
            "score": score,
            "category": category,
            "delay_risk": "High" if soil_type == "soft" else "Low",
            "volatility_risk": "Moderate" if price_drift > 0.03 else "Low"
        }
        
    def benchmark_cost(self, actual_cost: float, total_area_sqft: float) -> dict:
        """
        Compares actual projected cost with market benchmark.
        """
        cost_per_sqft = actual_cost / total_area_sqft
        market_benchmark = self.benchmarks.get(self.nation, 150)
        
        status = "Below Market Average ✅"
        if cost_per_sqft > market_benchmark * 1.1:
            status = "Above Market Average ⚠️"
        elif cost_per_sqft > market_benchmark:
            status = "Standard Market Rate ⚖️"
            
        return {
            "cost_per_sqft": round(cost_per_sqft, 2),
            "market_benchmark": market_benchmark,
            "status": status,
            "variance_pct": round(((cost_per_sqft - market_benchmark) / market_benchmark) * 100, 1)
        }

if __name__ == "__main__":
    risk = RiskIntelligenceEngine("india")
    print(risk.score_risk("hard", 2, 0.05))
    print(risk.benchmark_cost(1600000, 1000))
