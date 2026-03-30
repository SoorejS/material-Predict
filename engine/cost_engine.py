"""
CCIE Elite 6.5 Central Cost Engine
Final orchestration engine now incorporating the Financial Optimization Node.
"""

import logging
from engine.quantity_estimator import QuantityEstimator
from engine.material_mapper import MaterialMapper
from engine.time_simulator import TimeSimulator
from services.procurement import ProcurementAdvisor
from items.item_costs import ItemCostEstimator
from engine.uncertainty_engine import UncertaintyEngine
from services.optimizer import FinancialOptimizer

logger = logging.getLogger(__name__)

class EliteCostEngine:
    """
    V6.5 Elite Engine: Reconciles geometry, prices, and high-impact optimizations.
    """
    def __init__(self, width: float, length: float, floors: int = 1, soil: str = "hard", nation: str = "global"):
        self.estimator = QuantityEstimator(width, length, floors, soil)
        self.mapper = MaterialMapper()
        self.time_sim = TimeSimulator()
        self.ice = ItemCostEstimator(width * length * floors, floors + 2)
        self.optimizer = FinancialOptimizer(nation)
        self.nation = nation.lower()
        self.currency = "INR" if self.nation == "india" else "USD"
        self.soil = soil.lower()
        
    def generate_elite_boq(self, predictive_prices: dict, monthly_drift: float = 0.05) -> dict:
        """
        Input: Dynamic predictive prices.
        Output: Full Elite Construction Report with Optimizations (V6.5).
        """
        geom = self.estimator.estimate_segment_geometry()
        future_forecast = self.time_sim.forecast_lifecycle_costs(predictive_prices, monthly_drift)
        
        found_prices = future_forecast["Foundation"]
        struct_prices = future_forecast["Structural"]
        
        report = {
          "currency": self.currency,
          "built_area_sqft": geom["total_built_sqft"],
          "soil_type": self.soil,
          "segments": {},
          "procurement_advice": [],
          "uncertainty": {},
          "optimizations": []
        }
        
        # --- Phase 1: Foundation ---
        found_mats = self.mapper.concrete_to_mats(geom["foundation_m3"])
        steel_kg = self.mapper.area_to_steel(self.estimator.area_ft2) * 0.7 
        found_cost = (found_mats["cement_bags"] * found_prices.get("cement", 400)) + \
                     (steel_kg * found_prices.get("steel", 75))
                     
        report["segments"]["Foundation"] = {
          "cement_bags": found_mats["cement_bags"],
          "steel_kg": steel_kg,
          "cost": round(found_cost, 2),
          "phase": "Foundation (Phase 1)"
        }

        # --- Phase 2: Walls & Slabs ---
        wall_mats = self.mapper.masonry_to_mats(geom["wall_m3"])
        slab_mats = self.mapper.concrete_to_mats(geom["slab_m3"])
        slab_steel = self.mapper.area_to_steel(self.estimator.area_ft2 * self.estimator.floors)
        
        structural_cost = (wall_mats["bricks"] * struct_prices.get("bricks", 10.0)) + \
                          (wall_mats["mortar_cement_bags"] * struct_prices.get("cement", 400)) + \
                          (slab_mats["cement_bags"] * struct_prices.get("cement", 400)) + \
                          (slab_steel * struct_prices.get("steel", 75))
        
        report["segments"]["Structural Walls & Slab"] = {
          "bricks": wall_mats["bricks"],
          "cement_bags": round(wall_mats["mortar_cement_bags"] + slab_mats["cement_bags"], 1),
          "steel_kg": slab_steel,
          "cost": round(structural_cost, 2),
          "phase": "Structural (Phase 2)"
        }

        # --- Phase 3: Finishing ---
        items_rep = self.ice.estimate_item_costs()
        for item in items_rep["items"]:
            report["segments"][item["name"]] = {
              "qty": item["qty"],
              "cost": item["cost"],
              "phase": "Finishing (Phase 3)"
            }
            
        # --- Aggregation ---
        total_project_cost = sum(seg["cost"] for seg in report["segments"].values())
        report["total_cost"] = round(total_project_cost, 2)
        
        # --- V6.5 Node: Optimization Engine ---
        # Map material trends based on monthly drift (positive = up, negative = down/stable)
        trends = {"cement": monthly_drift, "steel": monthly_drift}
        report["optimizations"] = self.optimizer.generate_optimizations(report, trends)
        
        # Procurement & Uncertainty
        for mat in ["cement", "steel"]:
            advisor = ProcurementAdvisor(predictive_prices.get(mat), struct_prices.get(mat), 1.0)
            report["procurement_advice"].append(advisor.generate_strategy(mat))

        ue = UncertaintyEngine(total_project_cost, 0.4)
        report["uncertainty"] = ue.calculate_range(0.08)
        
        return report

if __name__ == "__main__":
    engine = EliteCostEngine(20, 30, 2, "hard", "india")
    prices = {"cement": 450, "steel": 78, "bricks": 12}
    print(engine.generate_elite_boq(prices, 0.05))
