import logging
from app.engine.quantity_estimator import StructuralQuantityEstimator
from app.engine.material_mapper import MaterialUnitMapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConstructionCostEngine:
    """
    Final Engine that ties predicted prices to estimated quantities.
    It takes material prices in local currency and outputs a segment-wise cost.
    """
    def __init__(self, plot_width: float, plot_length: float, floors: int = 1, soil: str = "hard"):
        self.estimator = StructuralQuantityEstimator(plot_width, plot_length, floors, soil)
        self.mapper = MaterialUnitMapper()
        
    def calculate_project_costs(self, prices: dict) -> dict:
        """
        Input: Dictionary of dynamic prices (e.g., {'cement': 400, 'steel': 75, 'bitumen': 50, ...})
        Output: Full segment-wise costing breakdown.
        """
        boq = self.estimator.generate_full_bill_of_quantities()
        project_costs = {
            "segments": {},
            "summary": {
                "total_cost": 0.0,
                "total_cement_bags": 0.0,
                "total_steel_kg": 0.0,
                "currency": prices.get("currency", "USD")
            }
        }
        
        # 1. Foundation Costs
        found = boq[0]
        found_mats = self.mapper.concrete_to_materials(found["volume_m3"])
        found_steel = self.mapper.built_area_to_steel(found["area_sqft"])
        
        # Assume 70% of area estimate to steel for foundation reinforcement
        found_cost = (found_mats["cement_bags"] * prices.get("cement", 500)) + \
                     (found_steel * 0.7 * prices.get("steel", 80))
        
        project_costs["segments"]["Foundation"] = {
            "cement_bags": found_mats["cement_bags"],
            "steel_kg": found_steel * 0.7,
            "cost": round(found_cost, 2)
        }
        
        # 2. Floor-wise Costs
        for f in range(1, len(boq)):
            floor_data = boq[f][f"Floor {f}"]
            
            # Wall Materials
            bricks_count = self.mapper.wall_to_bricks(floor_data["wall_vol_m3"])
            # Simplified wall cement estimation (1 bag per 100 bricks)
            wall_cement = bricks_count / 100.0
            
            # Slab Materials
            slab_mats = self.mapper.concrete_to_materials(floor_data["slab_vol_m3"])
            slab_steel = self.mapper.built_area_to_steel(floor_data["built_area_sqft"])
            
            floor_cost = (wall_cement * prices.get("cement", 500)) + \
                         (slab_mats["cement_bags"] * prices.get("cement", 500)) + \
                         (slab_steel * prices.get("steel", 80))
            
            project_costs["segments"][f"Floor {f}"] = {
                "built_area": floor_data["built_area_sqft"],
                "cement_bags": round(wall_cement + slab_mats["cement_bags"], 1),
                "steel_kg": slab_steel,
                "cost": round(floor_cost, 2)
            }
            
        # 3. Summing it up
        total_cost = sum(seg["cost"] for seg in project_costs["segments"].values())
        total_cement = sum(seg["cement_bags"] for seg in project_costs["segments"].values())
        total_steel = sum(seg.get("steel_kg", 0) for seg in project_costs["segments"].values())
        
        project_costs["summary"]["total_cost"] = round(total_cost, 2)
        project_costs["summary"]["total_cement_bags"] = round(total_cement, 0)
        project_costs["summary"]["total_steel_kg"] = round(total_steel, 0)
        
        logger.info(f"Full Project Costing Complete: {project_costs['summary']}")
        return project_costs

if __name__ == "__main__":
    engine = ConstructionCostEngine(20, 30, floors=2, soil="hard")
    # Simulation prices (INR)
    p = {'cement': 450, 'steel': 78, 'currency': 'INR'}
    print(engine.calculate_project_costs(p))
