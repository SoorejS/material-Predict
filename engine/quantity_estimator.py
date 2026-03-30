"""
CCIE Elite Quality Estimator Engine
Calculates structural volumes and areas for foundation, walls, and slabs.
"""

from engine.construction_rules import CONSTRUCTION_RULES

class QuantityEstimator:
    """
    Geometry-aware quantity estimator for a multi-floor building.
    Transforms plot dimensions into structural cubic meters (m3).
    """
    def __init__(self, width: float, length: float, floors: int = 1, soil: str = "hard"):
        self.width = width
        self.length = length
        self.floors = floors
        self.soil = soil.lower()
        self.rules = CONSTRUCTION_RULES
        
        # Calculate Footprints
        self.area_ft2 = width * length
        self.perimeter_ft = 2 * (width + length)
        
    def estimate_segment_geometry(self) -> dict:
        """
        Calculates geometric volumes for Foundation, Walls, and Slabs.
        """
        soil_factor = self.rules["soil_adjustment"].get(self.soil, 1.0)
        
        # 🧪 1. Foundation Calculation
        depth = self.rules["dimensions"]["foundation_base_ft"] * soil_factor
        found_vol_cft = self.perimeter_ft * 2.0 * depth  # 2.0ft wide footing
        
        # 🧱 2. Wall Calculation (External + Internal Partition Sim)
        # Assume internal partitioning is roughly 1.5x the external perimeter
        total_wall_len = self.perimeter_ft * 2.5 
        height = self.rules["dimensions"]["floor_height_ft"] * self.floors
        wall_thick = self.rules["dimensions"]["wall_thickness_ft"]
        wall_vol_cft = total_wall_len * height * wall_thick
        
        # 🏢 3. Slab Calculation
        slab_thick = self.rules["dimensions"]["slab_thickness_ft"]
        slab_vol_cft = self.area_ft2 * slab_thick * self.floors
        
        return {
            "foundation_m3": round(found_vol_cft * 0.02831, 2),
            "wall_m3": round(wall_vol_cft * 0.02831, 2),
            "slab_m3": round(slab_vol_cft * 0.02831, 2),
            "total_built_sqft": self.area_ft2 * self.floors
        }

if __name__ == "__main__":
    est = QuantityEstimator(20, 30, 2, "hard")
    print(est.estimate_segment_geometry())
