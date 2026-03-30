import logging
from data.construction_rules import CONSTRUCTION_RULES, SOIL_FACTORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StructuralQuantityEstimator:
    """
    Calculates structural quantities (Volumes/Areas) for a building segment-wise.
    Based on plot dimensions and floor counts.
    """
    def __init__(self, plot_width_ft: float, plot_length_ft: float, floors: int = 1, soil_type: str = "hard"):
        self.width = plot_width_ft
        self.length = plot_length_ft
        self.floors = floors
        self.soil_type = soil_type.lower()
        self.rules = CONSTRUCTION_RULES
        self.area_per_floor = self.width * self.length
        self.perimeter_ft = 2 * (self.width + self.length)
        
    def estimate_foundation(self) -> dict:
        """
        Calculates foundation volume based on soil type and plot footprint.
        """
        factor = SOIL_FACTORS.get(self.soil_type, 1.0)
        depth = self.rules["dimensions"]["foundation_depth_ft"] * factor
        
        # Assume foundation footprint is perimeter + cross-beams (simplified)
        vol_cft = self.perimeter_ft * 2.0 * depth  # 2ft width footing
        vol_m3 = vol_cft * 0.02831  # Convert to cubic meters
        
        return {
            "name": "Foundation",
            "volume_m3": round(vol_m3, 2),
            "area_sqft": self.area_per_floor
        }
        
    def estimate_floor_l1(self, floor_num: int) -> dict:
        """
        Calculates wall volume and slab volume for a single floor.
        """
        height = self.rules["dimensions"]["standard_wall_height_ft"]
        wall_thick = self.rules["dimensions"]["standard_wall_thickness_ft"]
        slab_thick = self.rules["dimensions"]["standard_slab_thickness_ft"]
        
        # Wall Volume (Perimeter x Height x Thickness)
        wall_vol_cft = self.perimeter_ft * height * wall_thick
        wall_vol_m3 = wall_vol_cft * 0.02831
        
        # Slab Volume (Area x Thickness)
        slab_vol_cft = self.area_per_floor * slab_thick
        slab_vol_m3 = slab_vol_cft * 0.02831
        
        return {
            f"Floor {floor_num}": {
                "wall_vol_m3": round(wall_vol_m3, 2),
                "slab_vol_m3": round(slab_vol_m3, 2),
                "built_area_sqft": self.area_per_floor
            }
        }

    def generate_full_bill_of_quantities(self) -> list:
        """
        Aggregates all segment-wise quantities.
        """
        segments = []
        segments.append(self.estimate_foundation())
        
        for f in range(1, self.floors + 1):
            segments.append(self.estimate_floor_l1(f))
            
        logger.info(f"Generated BoQ skeleton for {self.floors} floors on {self.soil_type} soil.")
        return segments

if __name__ == "__main__":
    # Test for 20x30 plot, 2 floors
    estimator = StructuralQuantityEstimator(20, 30, floors=2, soil_type="hard")
    print(estimator.generate_full_bill_of_quantities())
