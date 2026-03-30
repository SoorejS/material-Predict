"""
Construction Rules Engine: Defines standard civil engineering constants and conversion rules.
These rules are used to map structural volumes/areas to material quantities.
"""

CONSTRUCTION_RULES = {
    # Materials needed per unit of structural volume (m3)
    "m3_concrete": {
        "cement_kg": 350,      # Ordinary Portland Cement per m3
        "sand_m3": 0.45,       # Fine aggregate
        "aggregate_m3": 0.90,  # Coarse aggregate
    },
    
    # Common Structural Constants (per sqft or linear ft)
    "structural": {
        "steel_kg_per_sqft": 4.5,     # Reinforcement steel per built-up area
        "bricks_per_sqft_wall": 9.0,  # Number of standard bricks for a 9-inch wall
        "cement_bags_per_sqft": 0.4,  # Approximate cement bags per built area (total)
    },
    
    # Component Specific Assumptions
    "dimensions": {
        "standard_wall_height_ft": 10.0,
        "standard_slab_thickness_ft": 0.5,    # ~6 inches
        "standard_wall_thickness_ft": 0.75,   # ~9 inches
        "foundation_depth_ft": 5.0,
    },
    
    # Material Mapping for predicting prices
    "material_mapping": {
        "Cement": "cement",
        "Steel": "steel",
        "Bitumen": "bitumen",
        "Waterproofing": "waterproofing",
        "PVC": "pvc",
        "Aluminum": "aluminum"
    }
}

# Soil Correction Factors (Affects foundation cost)
SOIL_FACTORS = {
    "hard": 1.0,      # Hard/Stony soil (Less depth/reinforcement)
    "medium": 1.25,   # Medium/Normal soil
    "soft": 1.6,      # Soft/Silt soil (Deep foundation/Piling)
}
