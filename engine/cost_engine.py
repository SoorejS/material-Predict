"""
CCIE Elite Central Cost Engine
Final orchestration engine to reconcile quantities, prices, and items.
"""

import logging
from engine.quantity_estimator import QuantityEstimator
from engine.material_mapper import MaterialMapper
from engine.time_simulator import TimeSimulator
from services.procurement import ProcurementAdvisor
from items.item_costs import ItemCostEstimator
from engine.uncertainty_engine import UncertaintyEngine

logger = logging.getLogger(__name__)

class EliteCostEngine:
    """
    Orchestrates dimensions -> quantities -> prices -> items -> final BOQ.
    """
    def __init__(self, width: float, length: float, floors: int = 1, soil: str = "hard", nation: str = "global"):
        self.estimator = QuantityEstimator(width, length, floors, soil)
        self.mapper = MaterialMapper()
        self.time_sim = TimeSimulator()
        self.ice = ItemCostEstimator(width * length * floors, floors + 2)
        self.nation = nation.lower()
        self.currency = "INR" if self.nation == "india" else "USD"
        
    def generate_elite_boq(self, predictive_prices: dict, monthly_drift: float = 0.05) -> dict:
        """
        Input: Dynamic predictive prices from ML agents.
        Output: Full Elite Construction Report (v5.0 Ready).
        """
        # 1. Geometry Analysis
        geom = self.estimator.estimate_segment_geometry()
        
        # 2. Lifecycle Price Forecasting
        # Forecast prices for Foundation (Phase 1), Structural (Phase 2), Finishing (Phase 3)
        future_forecast = self.time_sim.forecast_lifecycle_costs(predictive_prices, monthly_drift)
        
        foundation_prices = future_forecast["Foundation"]
        structural_prices = future_forecast["Structural"]
        
        report = {
          "currency": self.currency,
          "built_area_sqft": geom["total_built_sqft"],
          "segments": {},
          "materials_summary": {},
          "procurement_advice": [],
          "uncertainty": {}
        }
        
        # --- PHASE 1: FOUNDATION ---
        found_mats = self.mapper.concrete_to_mats(geom["foundation_m3"])
        steel_kg = self.mapper.area_to_steel(self.estimator.area_ft2) * 0.7  # Foundation steel factor
        found_cost = (found_mats["cement_bags"] * foundation_prices.get("cement", 400)) + \
                     (steel_kg * foundation_prices.get("steel", 75))
                     
        report["segments"]["Foundation"] = {
          "cement_bags": found_mats["cement_bags"],
          "steel_kg": steel_kg,
          "cost": round(found_cost, 2),
          "phase": "Foundation (Phase 1)"
        }

        # --- PHASE 2: WALLS & SLABS ---
        wall_mats = self.mapper.masonry_to_mats(geom["wall_m3"])
        slab_mats = self.mapper.concrete_to_mats(geom["slab_m3"])
        slab_steel = self.mapper.area_to_steel(self.estimator.area_ft2 * self.estimator.floors)
        
        structural_cost = (wall_mats["bricks"] * structural_prices.get("bricks", 10.0)) + \
                          (wall_mats["mortar_cement_bags"] * structural_prices.get("cement", 400)) + \
                          (slab_mats["cement_bags"] * structural_prices.get("cement", 400)) + \
                          (slab_steel * structural_prices.get("steel", 75))
        
        report["segments"]["Structural Walls & Slab"] = {
          "bricks": wall_mats["bricks"],
          "cement_bags": round(wall_mats["mortar_cement_bags"] + slab_mats["cement_bags"], 1),
          "steel_kg": slab_steel,
          "cost": round(structural_cost, 2),
          "phase": "Structural (Phase 2)"
        }

        # --- PHASE 3: ITEMS & FINISHING ---
        items_report = self.ice.estimate_item_costs()
        # Add Finishing items to segments
        for item in items_report["items"]:
            report["segments"][item["name"]] = {
              "qty": item["qty"],
              "cost": item["cost"],
              "phase": "Finishing (Phase 3)"
            }
            
        # 3. PROCUREMENT INTELLIGENCE
        # Only advise on core materials like Cement and Steel
        for mat in ["cement", "steel"]:
            advisor = ProcurementAdvisor(predictive_prices.get(mat), structural_prices.get(mat), 1.0)
            advice = advisor.generate_strategy(mat)
            report["procurement_advice"].append(advice)

        # 4. FINAL PROJECT AGGREGATION & UNCERTAINTY
        total_project_cost = sum(seg["cost"] for seg in report["segments"].values())
        report["total_cost"] = round(total_project_cost, 2)
        
        # Uncertainty Engine (assuming 0.3 sentiment)
        ue = UncertaintyEngine(total_project_cost, 0.3)
        report["uncertainty"] = ue.calculate_range(0.08)
        
        return report

if __name__ == "__main__":
    engine = EliteCostEngine(20, 30, 2, "hard", "india")
    prices = {"cement": 450, "steel": 78, "bricks": 12}
    print(engine.generate_elite_boq(prices, 0.05))
