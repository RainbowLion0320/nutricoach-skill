#!/usr/bin/env python3
"""
Update food database with storage_method and default_shelf_life_days.
Note: food_group column has been removed, using category instead.
"""

import sqlite3
import os

# 食物储存方式和保质期数据库（基于食品安全标准）
# 数据来源：FDA、USDA、中国食品安全标准
FOOD_STORAGE_DATA = {
    # 蛋白质类
    '鸡胸肉': {'storage': '冰箱', 'group': 'protein', 'shelf_life': 2},
    '牛肉': {'storage': '冰箱', 'group': 'protein', 'shelf_life': 3},
    '猪肉': {'storage': '冰箱', 'group': 'protein', 'shelf_life': 3},
    '羊肉': {'storage': '冰箱', 'group': 'protein', 'shelf_life': 3},
    '三文鱼': {'storage': '冷冻', 'group': 'protein', 'shelf_life': 90},
    '虾仁': {'storage': '冷冻', 'group': 'protein', 'shelf_life': 90},
    '鸡蛋': {'storage': '冰箱', 'group': 'protein', 'shelf_life': 28},
    '豆腐': {'storage': '冰箱', 'group': 'protein', 'shelf_life': 5},
    '牛奶': {'storage': '冰箱', 'group': 'dairy', 'shelf_life': 7},
    '酸奶': {'storage': '冰箱', 'group': 'dairy', 'shelf_life': 14},
    '奶酪': {'storage': '冰箱', 'group': 'dairy', 'shelf_life': 14},

    # 蔬菜类
    '西兰花': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 5},
    '菠菜': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 5},
    '西红柿': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 7},
    '黄瓜': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 7},
    '胡萝卜': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 21},
    '土豆': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 60},
    '红薯': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 30},
    '洋葱': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 30},
    '大蒜': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 90},
    '生姜': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 30},
    '葱': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 14},
    '香菜': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 7},
    '芹菜': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 14},
    '白菜': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 14},
    '生菜': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 7},
    '茄子': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 7},
    '青椒': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 14},
    '辣椒': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 14},
    '南瓜': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 30},
    '冬瓜': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 30},
    '蘑菇': {'storage': '冰箱', 'group': 'vegetable', 'shelf_life': 5},
    '香菇': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 180},
    '木耳': {'storage': '干货区', 'group': 'vegetable', 'shelf_life': 365},

    # 碳水类
    '米饭': {'storage': '冰箱', 'group': 'carb', 'shelf_life': 2},
    '燕麦': {'storage': '干货区', 'group': 'carb', 'shelf_life': 365},
    '面条': {'storage': '干货区', 'group': 'carb', 'shelf_life': 365},
    '面粉': {'storage': '干货区', 'group': 'carb', 'shelf_life': 180},
    '糙米': {'storage': '干货区', 'group': 'carb', 'shelf_life': 365},
    '小米': {'storage': '干货区', 'group': 'carb', 'shelf_life': 365},
    '玉米': {'storage': '干货区', 'group': 'carb', 'shelf_life': 7},
    '面包': {'storage': '台面', 'group': 'carb', 'shelf_life': 5},
    '馒头': {'storage': '冰箱', 'group': 'carb', 'shelf_life': 3},
    '包子': {'storage': '冰箱', 'group': 'carb', 'shelf_life': 3},
    '饺子': {'storage': '冷冻', 'group': 'carb', 'shelf_life': 90},
    '馄饨': {'storage': '冷冻', 'group': 'carb', 'shelf_life': 90},

    # 水果类
    '苹果': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 30},
    '香蕉': {'storage': '台面', 'group': 'fruit', 'shelf_life': 7},
    '橙子': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 21},
    '葡萄': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 7},
    '西瓜': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 7},
    '草莓': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 5},
    '蓝莓': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 7},
    '芒果': {'storage': '台面', 'group': 'fruit', 'shelf_life': 7},
    '菠萝': {'storage': '台面', 'group': 'fruit', 'shelf_life': 5},
    '猕猴桃': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 14},
    '梨': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 21},
    '桃子': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 7},
    '樱桃': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 7},
    '柠檬': {'storage': '冰箱', 'group': 'fruit', 'shelf_life': 21},
    '柚子': {'storage': '台面', 'group': 'fruit', 'shelf_life': 14},

    # 脂肪类
    '橄榄油': {'storage': '干货区', 'group': 'fat', 'shelf_life': 365},
    '花生油': {'storage': '干货区', 'group': 'fat', 'shelf_life': 365},
    '菜籽油': {'storage': '干货区', 'group': 'fat', 'shelf_life': 365},
    '黄油': {'storage': '冰箱', 'group': 'fat', 'shelf_life': 90},
    '花生酱': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '芝麻酱': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '坚果': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '杏仁': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '核桃': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '腰果': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '花生': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '瓜子': {'storage': '干货区', 'group': 'fat', 'shelf_life': 180},
    '牛油果': {'storage': '台面', 'group': 'fat', 'shelf_life': 5},
}

# 分类映射规则
CATEGORY_MAPPING = {
    # 蛋白质
    'beef': 'protein', 'pork': 'protein', 'poultry': 'protein', 'seafood': 'protein',
    'egg': 'protein', 'soy': 'protein', 'protein': 'protein', 'meat': 'protein',

    # 蔬菜
    'vegetable': 'vegetable', 'mushroom': 'vegetable', 'seaweed': 'vegetable',

    # 碳水
    'grain': 'carb', 'starch': 'carb',

    # 水果
    'fruit': 'fruit',

    # 乳制品
    'dairy': 'dairy',

    # 脂肪
    'fat': 'fat', 'oil': 'fat', 'nut': 'fat',

    # 其他默认
    'snack': 'carb', 'condiment': 'fat', 'beverage': 'fruit',
}

# 默认储存方式映射
DEFAULT_STORAGE = {
    'protein': '冰箱',
    'vegetable': '冰箱',
    'carb': '干货区',
    'fruit': '冰箱',
    'dairy': '冰箱',
    'fat': '干货区',
}

# 默认保质期（天）
DEFAULT_SHELF_LIFE = {
    'protein': 3,
    'vegetable': 7,
    'carb': 180,
    'fruit': 14,
    'dairy': 7,
    'fat': 180,
}


def get_food_info(food_name, current_category):
    """Get storage method and shelf life for a food."""
    # 直接匹配
    if food_name in FOOD_STORAGE_DATA:
        data = FOOD_STORAGE_DATA[food_name]
        return data['storage'], data['shelf_life']

    # 根据当前 category 映射
    food_group = CATEGORY_MAPPING.get(current_category, 'carb')
    storage = DEFAULT_STORAGE.get(food_group, '干货区')
    shelf_life = DEFAULT_SHELF_LIFE.get(food_group, 30)

    return storage, shelf_life


def update_database(db_path):
    """Update database schema and populate new fields."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if columns exist
    cursor.execute("PRAGMA table_info(custom_foods)")
    columns = [col[1] for col in cursor.fetchall()]

    # Add new columns if they don't exist
    if 'storage_method' not in columns:
        cursor.execute("ALTER TABLE custom_foods ADD COLUMN storage_method TEXT")
        print("Added: storage_method")

    if 'default_shelf_life_days' not in columns:
        cursor.execute("ALTER TABLE custom_foods ADD COLUMN default_shelf_life_days INTEGER")
        print("Added: default_shelf_life_days")

    # Update existing records
    cursor.execute("SELECT id, name, category FROM custom_foods")
    foods = cursor.fetchall()

    updated = 0
    for food_id, name, category in foods:
        storage, shelf_life = get_food_info(name, category)

        cursor.execute("""
            UPDATE custom_foods
            SET storage_method = ?,
                default_shelf_life_days = ?
            WHERE id = ?
        """, (storage, shelf_life, food_id))
        updated += 1

    conn.commit()
    conn.close()

    print(f"\nUpdated {updated} food records")
    print("\nSummary by category:")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, storage_method, COUNT(*) as count,
               AVG(default_shelf_life_days) as avg_shelf_life
        FROM custom_foods
        GROUP BY category, storage_method
        ORDER BY category, storage_method
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]} / {row[1]}: {row[2]} items, avg {row[3]:.0f} days")
    conn.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', required=True, help='Username')
    args = parser.parse_args()

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(skill_dir, 'data', f'{args.user}.db')

    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        sys.exit(1)

    update_database(db_path)
    print(f"\nDatabase updated: {db_path}")