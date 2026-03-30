import logging
from app.engine.quantity_estimator import StructuralQuantityEstimator
from app.engine.material_mapper import MaterialUnitMapper
from app.engine.floor_parser import FloorPlanParser
from app.engine.procurement_advisor import ProcurementAdvisor
from app.engine.risk_engine import RiskIntelligenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConstructionCostEngine:
    """
    Elite V5.0 Cost Engine: 
    Includes Geometry, Time-Based Costs, Procurement Recommendations, and Risk Intelligence.
    """
    def __init__(self, plot_width: float, plot_length: float, floors: int = 1, soil: str = "hard", nation: str = "global"):
        self.estimator = StructuralQuantityEstimator(plot_width, plot_length, floors, soil)
        self.mapper = MaterialUnitMapper()
        self.parser = FloorPlanParser(plot_width * plot_length)
        self.advisor = ProcurementAdvisor()
        self.risk_intel = RiskIntelligenceEngine(nation)
        self.area = plot_width * plot_length
        self.floors = floors
        self.soil = soil
        
    def calculate_project_costs(self, prices: dict, monthly_drift: float = 0.05) -> dict:
        """
        Input: Dynamic Preise + ML Trend (Drift).
        Output: Full Decision Intelligence Suite.
        """
        boq = self.estimator.generate_full_bill_of_quantities()
        project_costs = {
            "segments": {},
            "summary": {
                "total_cost": 0.0,
                "total_cement_bags": 0.0,
                "total_steel_kg": 0.0,
                "currency": prices.get("currency", "USD"),
                "confidence_interval": "±10%",
                "cost_min": 0.0,
                "cost_max": 0.0
            },
            "procurement_advice": [],
            "risk_analysis": {}
        }
        
        # 1. Foundation Costs (Month 1 Price)
        found = boq[0]
        found_mats = self.mapper.concrete_to_materials(found["volume_m3"])
        found_steel = self.mapper.built_area_to_steel(found["area_sqft"])
        
        found_cost = (found_mats["cement_bags"] * prices.get("cement", 500)) + \
                     (found_steel * 0.7 * prices.get("steel", 80))
        
        project_costs["segments"]["Foundation"] = {
            "cement_bags": found_mats["cement_bags"],
            "steel_kg": found_steel * 0.7,
            "cost": round(found_cost, 2),
            "phase": "Month 1 (Current)"
        }
        
        # 2. Floor-wise Costs (Month 3 Forecast Price)
        p_cement_m3 = prices.get("cement", 500) * (1 + monthly_drift)**2
        p_steel_m3 = prices.get("steel", 80) * (1 + monthly_drift)**2
        
        total_structural_steel = 0.0
        
        for f in range(1, len(boq)):
            floor_data = boq[f][f"Floor {f}"]
            geometry = self.parser.parse_rooms(f)
            total_wall_len_ft = self.estimator.perimeter_ft + geometry["internal_wall_ft"]
            
            height = self.estimator.rules["dimensions"]["standard_wall_height_ft"]
            wall_thick = self.estimator.rules["dimensions"]["standard_wall_thickness_ft"]
            real_wall_vol_m3 = (total_wall_len_ft * height * wall_thick) * 0.02831
            
            bricks_count = self.mapper.wall_to_bricks(real_wall_vol_m3)
            wall_cement = bricks_count / 100.0  # 1 bag per 100 bricks
            slab_mats = self.mapper.concrete_to_materials(floor_data["slab_vol_m3"])
            slab_steel = self.mapper.built_area_to_steel(floor_data["built_area_sqft"])
            
            floor_cost = (wall_cement * p_cement_m3) + \
                         (slab_mats["cement_bags"] * p_cement_m3) + \
                         (slab_steel * p_steel_m3)
            
            total_structural_steel += slab_steel
            
            project_costs["segments"][f"Floor {f}"] = {
                "num_rooms": geometry["num_rooms"],
                "cement_bags": round(wall_cement + slab_mats["cement_bags"], 1),
                "steel_kg": slab_steel,
                "cost": round(floor_cost, 2),
                "phase": "Month 3 (Forecast)"
            }
            
        # 3. Decision Intelligence: Procurement & Risks
        # Analyze steel procurement (Month 3 use vs Month 1 purchase)
        steel_advice = self.advisor.analyze_procurement(prices.get("steel", 80), monthly_drift, total_structural_steel)
        steel_advice["material"] = "Steel"
        project_costs["procurement_advice"].append(steel_advice)
        
        cement_advice = self.advisor.analyze_procurement(prices.get("cement", 500), monthly_drift, total_cement := 0.0)
        # Recalculate cement totals for advice
        total_cement = sum(seg["cement_bags"] for seg in project_costs["segments"].values())
        cement_advice["material"] = "Cement"
        cement_advice["potential_savings"] = round((p_cement_m3 - prices.get("cement", 500)) * total_cement, 2)
        project_costs["procurement_advice"].append(cement_advice)
        
        # Risk & Benchmarking
        project_costs["risk_analysis"] = self.risk_intel.score_risk(self.soil, self.floors, monthly_drift)
        
        # 4. Final Aggregation
        total_cost = sum(seg["cost"] for seg in project_costs["segments"].values())
        project_costs["summary"]["total_cost"] = round(total_cost, 2)
        project_costs["summary"]["total_cement_bags"] = round(total_cement, 0)
        project_costs["summary"]["total_steel_kg"] = round(total_structural_steel + (found_steel * 0.7), 0)
        project_costs["summary"]["cost_min"] = round(total_cost * 0.9, 2)
        project_costs["summary"]["cost_max"] = round(total_cost * 1.1, 2)
        
        # Benchmarking
        bench = self.risk_intel.benchmark_cost(total_cost, self.area * self.floors)
        project_costs["risk_analysis"].update(bench)
        
        logger.info(f"V5.0 Elite Intelligence Complete: {project_costs['summary']}")
        return project_costs

if __name__ == "__main__":
    engine = ConstructionCostEngine(20, 30, floors=2, soil="hard", nation="india")
    p = {'cement': 450, 'steel': 78, 'currency': 'INR'}
    print(engine.calculate_project_costs(p, 0.05))
