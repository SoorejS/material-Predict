"""
CCIE Elite Engineering Rules Engine
Defines standard civil engineering constants, conversion factors, and architectural assumptions.
"""

CONSTRUCTION_RULES = {
    # 🔗 Concrete Mix Ratios (M20 Standard)
    "concrete": {
        "cement_kg_per_m3": 350.0,
        "sand_m3_per_m3": 0.45,
        "aggregate_m3_per_m3": 0.90,
        "dry_vol_multiplier": 1.54,   # Engineering constant for wet-to-dry conversion
    },
    
    # 🏢 Structural Quantities
    "structural": {
        "steel_kg_per_sqft": 4.5,      # Avg for residential RCC
        "bricks_per_sqft_wall": 9.0,   # 9-inch wall assumption
        "mortar_ratio": 0.25,          # Mortar volume per wall volume
    },
    
    # 📏 Architectural Dimensions
    "dimensions": {
        "floor_height_ft": 10.5,       # Standard residential height
        "slab_thickness_ft": 0.45,     # ~5.5 inches
        "wall_thickness_ft": 0.75,     # Standard 9-inch brick wall
        "foundation_base_ft": 5.0,     # Depth of excavation
    },
    
    # 🌍 Environmental Factors
    "soil_adjustment": {
        "hard": 1.0,
        "medium": 1.3,
        "soft": 1.6                   # +60% material/labor for soft/piling
    }
}

# Material-to-Ticker database mapping
MATERIAL_TICKERS = {
    "cement": "ULTRACEMCO.NS",
    "steel": "TATASTEEL.NS",
    "bricks": "VMC",             # Proxy for masonry/aggregates
    "paint": "BERGEPAINT.NS",
    "waterproofing": "CSL"
}
