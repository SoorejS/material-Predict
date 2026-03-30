import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FloorPlanParser:
    """
    Simulates a floor plan parser that decomposes a given area into rooms.
    Calculates internal wall lengths and partition requirements.
    """
    def __init__(self, total_area: float):
        self.total_area = total_area
        
    def parse_rooms(self, floor_num: int) -> dict:
        """
        Input: Total Floor Area.
        Output: Room-wise decomposition and total Internal Wall Length.
        """
        # Architectural Assumptions (Standard Villa Layout)
        # 1. Standard Room Size (120 sqft)
        # 2. Living Area (30% of total)
        # 3. Kitchen/Baths (20% of total)
        
        living_area = self.total_area * 0.3
        utility_area = self.total_area * 0.2
        bedroom_area = self.total_area - living_area - utility_area
        
        # Estimate number of rooms (Standard 12x10 bedroom ~ 120sqft)
        num_rooms = max(1, round(bedroom_area / 120))
        
        # Calculate Internal Initial Wall Length:
        # Every room adds roughly 2 internal wall segments (approx 12ft each)
        internal_wall_ft = num_rooms * 24.0 + (living_area / 10.0)
        
        logger.info(f"Floor {floor_num} Parsed: {num_rooms} Rooms, Internal Wall: {internal_wall_ft:.2f}ft")
        
        return {
            "num_rooms": num_rooms,
            "internal_wall_ft": round(internal_wall_ft, 2),
            "living_sqft": round(living_area, 2),
            "utility_sqft": round(utility_area, 2)
        }

if __name__ == "__main__":
    parser = FloorPlanParser(1000)
    print(parser.parse_rooms(1))
