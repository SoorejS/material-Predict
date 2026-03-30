import logging
from app.engine.quantity_estimator import StructuralQuantityEstimator
from app.engine.material_mapper import MaterialUnitMapper
from app.engine.floor_parser import FloorPlanParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConstructionCostEngine:
    """
    Elite Cost Engine: 
    Includes Geometry Analysis (Internal Walls), Time-Based Costs, and Uncertainty Intervals.
    """
    def __init__(self, plot_width: float, plot_length: float, floors: int = 1, soil: str = "hard"):
        self.estimator = StructuralQuantityEstimator(plot_width, plot_length, floors, soil)
        self.mapper = MaterialUnitMapper()
        self.parser = FloorPlanParser(plot_width * plot_length)
        
    def calculate_project_costs(self, prices: dict, monthly_drift: float = 0.05) -> dict:
        """
        Input: Dynamic Preise + ML Trend (Drift).
        Output: Full Elite Cost Analysis.
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
            }
        }
        
        # 1. Foundation Costs (Month 1 Price)
        found = boq[0]
        found_mats = self.mapper.concrete_to_materials(found["volume_m3"])
        found_steel = self.mapper.built_area_to_steel(found["area_sqft"])
        
        # Current month price for foundation
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
        
        for f in range(1, len(boq)):
            floor_data = boq[f][f"Floor {f}"]
            
            # Geometry Analysis: Extract Internal Rooms/Walls
            geometry = self.parser.parse_rooms(f)
            # Wall Length = Perimeter + Internal Walls
            total_wall_len_ft = self.estimator.perimeter_ft + geometry["internal_wall_ft"]
            
            # Recalculate Wall Volume with Internal Partitions
            height = self.estimator.rules["dimensions"]["standard_wall_height_ft"]
            wall_thick = self.estimator.rules["dimensions"]["standard_wall_thickness_ft"]
            real_wall_vol_m3 = (total_wall_len_ft * height * wall_thick) * 0.02831
            
            # Wall Materials
            bricks_count = self.mapper.wall_to_bricks(real_wall_vol_m3)
            wall_cement = bricks_count / 100.0  # 1 bag per 100 bricks
            
            # Slab Materials
            slab_mats = self.mapper.concrete_to_materials(floor_data["slab_vol_m3"])
            slab_steel = self.mapper.built_area_to_steel(floor_data["built_area_sqft"])
            
            # Use Month 3 Forecast Prices for Structural Phase
            floor_cost = (wall_cement * p_cement_m3) + \
                         (slab_mats["cement_bags"] * p_cement_m3) + \
                         (slab_steel * p_steel_m3)
            
            project_costs["segments"][f"Floor {f}"] = {
                "num_rooms": geometry["num_rooms"],
                "cement_bags": round(wall_cement + slab_mats["cement_bags"], 1),
                "steel_kg": slab_steel,
                "cost": round(floor_cost, 2),
                "phase": "Month 3 (Forecast)"
            }
            
        # 3. Summing it up and Uncertainty
        total_cost = sum(seg["cost"] for seg in project_costs["segments"].values())
        total_cement = sum(seg["cement_bags"] for seg in project_costs["segments"].values())
        total_steel = sum(seg.get("steel_kg", 0) for seg in project_costs["segments"].values())
        
        project_costs["summary"]["total_cost"] = round(total_cost, 2)
        project_costs["summary"]["total_cement_bags"] = round(total_cement, 0)
        project_costs["summary"]["total_steel_kg"] = round(total_steel, 0)
        
        # Uncertainty Engine (±10% based on ML confidence)
        project_costs["summary"]["cost_min"] = round(total_cost * 0.9, 2)
        project_costs["summary"]["cost_max"] = round(total_cost * 1.1, 2)
        
        logger.info(f"Elite Analytics Project Costing Complete: {project_costs['summary']}")
        return project_costs

if __name__ == "__main__":
    engine = ConstructionCostEngine(20, 30, floors=2, soil="hard")
    p = {'cement': 450, 'steel': 78, 'currency': 'INR'}
    print(engine.calculate_project_costs(p, 0.05))
