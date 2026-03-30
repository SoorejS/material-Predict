"""
CCIE Elite Item Costs Catalog
Detailed cost catalog for fixed architectural items (Windows, Doors, Paintings).
"""

ITEM_CATALOG = {
    "exterior_window_2x4": {
        "material": "PVC Frame + Float Glass",
        "components": ["Frame", "Glass", "Hinges", "Screws"],
        "unit_cost": 5500.0,
        "type": "Opening"
    },
    "internal_door_standard": {
        "material": "Flush Door + Teak Finish",
        "components": ["Door", "Frame", "Handle", "Lock"],
        "unit_cost": 8500.0,
        "type": "Opening"
    },
    "main_entrance_door": {
        "material": "Ghana Teak Wood",
        "components": ["Carved Panel", "Heavy Frame", "Brass Fittings"],
        "unit_cost": 22000.0,
        "type": "Opening"
    },
    "finishing": {
        "wall_paint_per_sqft": 45.0,        # Material + Labor
        "waterproofing_per_sqft": 65.0,      # Bituminous + Chemical
        "flooring_tile_per_sqft": 110.0      # Vitrified Tiles (Medium Grade)
    }
}

class ItemCostEstimator:
    """
    Calculates costs for non-structural built-in items based on area.
    """
    def __init__(self, built_area: float, rooms: int):
        self.area = built_area
        self.rooms = rooms
        
    def estimate_item_costs(self) -> dict:
        """
        Estimates quantity of Windows, Doors, and Painting areas.
        """
        # Architectural Rule of Thumb: 
        # 1 Window per room + 2 for living
        num_windows = self.rooms + 2
        num_doors = self.rooms + 1
        
        window_total = num_windows * ITEM_CATALOG["exterior_window_2x4"]["unit_cost"]
        door_total = (num_doors - 1) * ITEM_CATALOG["internal_door_standard"]["unit_cost"] + ITEM_CATALOG["main_entrance_door"]["unit_cost"]
        
        # Walls Area ~ 2.5x the floor area (built-up)
        painting_area = self.area * 2.5
        painting_total = painting_area * ITEM_CATALOG["finishing"]["wall_paint_per_sqft"]
        
        return {
          "items": [
            {"name": "Exterior Windows", "qty": num_windows, "cost": round(window_total, 2)},
            {"name": "Internal Doors", "qty": num_doors - 1, "cost": round(door_total, 2)},
            {"name": "Internal Painting", "qty": painting_area, "cost": round(painting_total, 2)}
          ],
          "item_total": round(window_total + door_total + painting_total, 2)
        }

if __name__ == "__main__":
    ice = ItemCostEstimator(600, 2)
    print(ice.estimate_item_costs())
