"""
Database Schema Definitions
Centralized column indices to avoid hardcoding throughout the codebase.
"""

# ============================================================================
# Users Table
# ============================================================================
USERS_COLUMNS = {
    'id': 0,
    'username': 1,
    'name': 2,
    'gender': 3,
    'birth_date': 4,
    'height_cm': 5,
    'target_weight_kg': 6,
    'activity_level': 7,
    'goal_type': 8,
    'bmr': 9,
    'tdee': 10,
    'created_at': 11,
    'updated_at': 12,
}

# ============================================================================
# Body Metrics Table - for SELECT recorded_at, weight_kg, bmi, body_fat_pct, notes
# ============================================================================
BODY_METRICS_COLUMNS = {
    'recorded_at': 0,
    'weight_kg': 1,
    'bmi': 2,
    'body_fat_pct': 3,
    'notes': 4,
}

# ============================================================================
# Custom Foods Table
# ============================================================================
CUSTOM_FOODS_COLUMNS = {
    'id': 0,
    'user_id': 1,
    'name': 2,
    'category': 3,
    'calories_per_100g': 4,
    'protein_per_100g': 5,
    'carbs_per_100g': 6,
    'fat_per_100g': 7,
    'fiber_per_100g': 8,
    'barcode': 9,
    'storage_method': 10,
    'food_group': 11,
    'default_shelf_life_days': 12,
    'created_at': 13,
}

# ============================================================================
# Meals Table
# ============================================================================
MEALS_COLUMNS = {
    'id': 0,
    'user_id': 1,
    'meal_type': 2,
    'eaten_at': 3,
    'notes': 4,
    'total_calories': 5,
    'total_protein_g': 6,
    'total_carbs_g': 7,
    'total_fat_g': 8,
}

# ============================================================================
# Food Items Table (meal_foods)
# ============================================================================
FOOD_ITEMS_COLUMNS = {
    'id': 0,
    'meal_id': 1,
    'food_id': 2,
    'food_name': 3,
    'quantity_g': 4,
    'calories': 5,
    'protein_g': 6,
    'carbs_g': 7,
    'fat_g': 8,
}

# ============================================================================
# Pantry Table - Column indices for SELECT queries
# Note: These map to query column positions, not table schema positions
# ============================================================================
PANTRY_COLUMNS = {
    'id': 0,
    'food_name': 1,
    'quantity_g': 2,
    'remaining_g': 3,
    'quantity_desc': 4,
    'location': 5,
    'purchase_date': 6,
    'expiry_date': 7,
    # Joined columns from custom_foods:
    'calories_per_100g': 8,
    'protein_per_100g': 9,
    'food_group': 10,
}

# ============================================================================
# Pantry Usage Table
# ============================================================================
PANTRY_USAGE_COLUMNS = {
    'id': 0,
    'pantry_id': 1,
    'user_id': 2,
    'used_g': 3,
    'remaining_after_g': 4,
    'used_for_meal_id': 5,
    'notes': 6,
    'used_at': 7,
}


def get_col(table: str, column: str) -> int:
    """Get column index for a table."""
    tables = {
        'users': USERS_COLUMNS,
        'body_metrics': BODY_METRICS_COLUMNS,
        'custom_foods': CUSTOM_FOODS_COLUMNS,
        'meals': MEALS_COLUMNS,
        'food_items': FOOD_ITEMS_COLUMNS,
        'pantry': PANTRY_COLUMNS,
        'pantry_usage': PANTRY_USAGE_COLUMNS,
    }
    if table not in tables:
        raise ValueError(f"Unknown table: {table}")
    if column not in tables[table]:
        raise ValueError(f"Unknown column {column} in table {table}")
    return tables[table][column]


# ============================================================================
# Default Values
# ============================================================================
DEFAULTS = {
    'user_height_cm': 170.0,
    'location_shelf_life': {
        'fridge': 7,
        'freezer': 90,
        'pantry': 30,
        'counter': 5,
    },
    'macro_split': {
        'protein_pct': 30,
        'carbs_pct': 40,
        'fat_pct': 30,
    },
}

# ============================================================================
# Activity Multipliers for TDEE Calculation
# ============================================================================
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}

# ============================================================================
# Goal Adjustments
# ============================================================================
GOAL_ADJUSTMENTS = {
    'lose': -500,  # Calorie deficit
    'maintain': 0,
    'gain': 300,   # Calorie surplus
}
