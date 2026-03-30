import logging
from data.construction_rules import CONSTRUCTION_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaterialUnitMapper:
    """
    Transforms structural volumes (m3) into actual material units (Cement Bags, Steel Kg, Bricks).
    """
    def __init__(self):
        self.rules = CONSTRUCTION_RULES
        
    def concrete_to_materials(self, vol_m3: float) -> dict:
        """
        Input: Volume in cubic meters (Concrete).
        Output: Mapping of Cement (Bags), Sand (m3), Aggregate (m3).
        """
        # Assume 1 Bag of Cement = 50kg
        cement_kg = vol_m3 * self.rules["m3_concrete"]["cement_kg"]
        cement_bags = cement_kg / 50.0
        
        sand_m3 = vol_m3 * self.rules["m3_concrete"]["sand_m3"]
        agg_m3 = vol_m3 * self.rules["m3_concrete"]["aggregate_m3"]
        
        return {
            "cement_bags": round(cement_bags, 1),
            "sand_m3": round(sand_m3, 2),
            "aggregate_m3": round(agg_m3, 2)
        }
        
    def built_area_to_steel(self, area_sqft: float) -> float:
        """
        Input: Total built area.
        Output: Steel Quantity in Kg.
        """
        steel_kg = area_sqft * self.rules["structural"]["steel_kg_per_sqft"]
        return round(steel_kg, 0)
        
    def wall_to_bricks(self, wall_vol_m3: float) -> int:
        """
        Input: Wall Volume in m3.
        Output: Number of standard bricks.
        """
        wall_vol_sqft = wall_vol_m3 / 0.02831  # convert back to cft
        # Simplified: Number of bricks per sqft (at standard thickness)
        bricks = wall_vol_sqft * self.rules["structural"]["bricks_per_sqft_wall"]
        return int(bricks)

if __name__ == "__main__":
    mapper = MaterialUnitMapper()
    print(mapper.concrete_to_materials(10.0))
    print(mapper.built_area_to_steel(600))
