"""
CCIE Elite Material Mapper Logic
Converts structural volumes (m3) into material bags, tonnes, and units.
"""

from engine.construction_rules import CONSTRUCTION_RULES

class MaterialMapper:
    """
    Transforms construction volumes (concretes/masonry) into material units.
    """
    def __init__(self):
        self.rules = CONSTRUCTION_RULES
        
    def concrete_to_mats(self, vol_m3: float) -> dict:
        """
        Maps concrete volume to Cement Bags and aggregate volumes.
        """
        # Assume standard 1:2:4 mix (M20)
        # Wet volume (actual) to dry volume conversion
        dry_vol = vol_m3 * self.rules["concrete"]["dry_vol_multiplier"]
        
        cement_kg = dry_vol * self.rules["concrete"]["cement_kg_per_m3"]
        cement_bags = cement_kg / 50.0  # Standard 50kg bag
        
        sand_m3 = dry_vol * self.rules["concrete"]["sand_m3_per_m3"]
        agg_m3 = dry_vol * self.rules["concrete"]["aggregate_m3_per_m3"]
        
        return {
          "cement_bags": round(cement_bags, 1),
          "sand_m3": round(sand_m3, 2),
          "aggregate_m3": round(agg_m3, 2)
        }
        
    def masonry_to_mats(self, vol_m3: float) -> dict:
        """
        Maps wall volume to bricks and cement for mortar.
        """
        bricks = vol_m3 * 450.0  # Approx 450 bricks per m3 (9-inch wall)
        # Assume 1/4 of masonry is mortar volume
        mortar_vol = vol_m3 * 0.25
        mortar_mats = self.concrete_to_mats(mortar_vol)
        
        return {
          "bricks": int(bricks),
          "mortar_cement_bags": mortar_mats["cement_bags"]
        }
        
    def area_to_steel(self, built_area_sqft: float) -> float:
        """
        Maps built area to reinforcement steel requirements in Kg.
        """
        steel_kg = built_area_sqft * self.rules["structural"]["steel_kg_per_sqft"]
        return round(steel_kg, 1)

if __name__ == "__main__":
    mm = MaterialMapper()
    print(mm.concrete_to_mats(10.0))
    print(mm.masonry_to_mats(10.0))
