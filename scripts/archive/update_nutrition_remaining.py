#!/usr/bin/env python3
"""
批量更新剩余食材的营养成分数据
根据类别设置合理的默认值
"""

import sqlite3
import sys
from pathlib import Path

# 按类别设置默认营养值
CATEGORY_DEFAULTS = {
    "beverage": (5, 0, 0, 0.5, 0, 0, 0.1, 0.05),  # 饮料
    "carb": (15, 0, 0.5, 1.0, 0, 0, 0.8, 0.5),    # 谷物
    "condiment": (30, 0, 0.2, 2.0, 10, 2, 1.5, 0.3),  # 调味料
    "dairy": (120, 0, 2.0, 5.0, 40, 0, 0.1, 0.4),  # 奶制品
    "egg": (50, 0, 2.5, 0.6, 100, 0, 1.5, 1.0),    # 蛋类
    "fruit": (15, 0, 0.05, 8.0, 10, 20, 0.3, 0.1),  # 水果
    "grain": (15, 0, 0.5, 1.0, 0, 0, 0.8, 0.5),    # 主食
    "lamb": (8, 0, 3.0, 0, 10, 0, 1.7, 2.8),       # 羊肉
    "meat": (10, 0, 2.0, 0, 10, 0, 2.0, 2.0),      # 其他肉类
    "mushroom": (5, 0, 0.05, 1.0, 2, 2, 0.8, 0.6),  # 菌菇
    "nut": (100, 0, 8.0, 3.0, 5, 1, 2.5, 3.0),     # 坚果
    "oil": (0, 0, 13.0, 0, 0, 0, 0.05, 0.01),      # 油脂
    "pork": (6, 0, 5.0, 0, 10, 0, 1.0, 1.5),       # 猪肉
    "poultry": (10, 0, 2.5, 0, 12, 0, 0.8, 1.0),   # 禽肉
    "protein": (15, 0, 1.0, 1.0, 10, 0, 1.5, 1.0), # 蛋白质类
    "seafood": (35, 0, 0.5, 0.3, 20, 1, 1.0, 0.8), # 海鲜
    "seaweed": (150, 0, 0.3, 0.5, 50, 5, 15.0, 1.5), # 海藻
    "snack": (25, 0.1, 6.0, 15.0, 30, 1, 1.2, 0.6), # 零食
    "soy": (80, 0, 1.0, 2.0, 5, 0, 3.5, 1.0),      # 豆制品
    "starch": (20, 0, 0.1, 1.0, 5, 8, 0.5, 0.3),   # 淀粉类
    "vegetable": (40, 0, 0.05, 2.5, 50, 25, 0.8, 0.3), # 蔬菜
    "beef": (6, 0, 3.0, 0, 8, 0, 1.8, 3.5),        # 牛肉
    "零食": (25, 0.1, 6.0, 15.0, 30, 1, 1.2, 0.6),  # 零食(中文)
}

def update_remaining_foods(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有未更新的食材
    cursor.execute("""
        SELECT id, name, category FROM custom_foods 
        WHERE calcium_mg = 0 AND trans_fat_g = 0 AND saturated_fat_g = 0 
        AND sugar_g = 0 AND vitamin_a_ug = 0 AND vitamin_c_mg = 0 
        AND iron_mg = 0 AND zinc_mg = 0
    """)
    
    remaining = cursor.fetchall()
    
    sql = """
    UPDATE custom_foods 
    SET calcium_mg = ?,
        trans_fat_g = ?,
        saturated_fat_g = ?,
        sugar_g = ?,
        vitamin_a_ug = ?,
        vitamin_c_mg = ?,
        iron_mg = ?,
        zinc_mg = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    
    updated_count = 0
    no_category = []
    
    for food_id, name, category in remaining:
        if category in CATEGORY_DEFAULTS:
            values = CATEGORY_DEFAULTS[category]
            cursor.execute(sql, (*values, food_id))
            updated_count += cursor.rowcount
        else:
            no_category.append((name, category))
    
    conn.commit()
    conn.close()
    
    return updated_count, no_category, len(remaining)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_nutrition_remaining.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    db_path = Path(__file__).parent.parent / "data" / f"{username}.db"
    
    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    print(f"Updating remaining nutrition data for {username}...")
    print(f"Database: {db_path}")
    print()
    
    updated, no_category, total = update_remaining_foods(db_path)
    
    print(f"Total remaining: {total}")
    print(f"✓ Updated with category defaults: {updated}")
    if no_category:
        print(f"✗ No category match: {len(no_category)} foods")
        for name, cat in no_category[:10]:
            print(f"  - {name} ({cat})")
        if len(no_category) > 10:
            print(f"  ... and {len(no_category) - 10} more")
