#!/usr/bin/env python3
"""
联网校对食材营养成分数据
更新新增营养成分字段：钙、反式脂肪、饱和脂肪、糖、维生素A、维生素C、铁、锌
数据来源：USDA FoodData Central、中国食物成分表标准版
"""

import sqlite3
import sys
from pathlib import Path

# 营养成分数据库 - 基于USDA和中国食物成分表的标准数据
# 单位：每100g可食部
NUTRITION_DATA = {
    # ===== 谷物类 (grain) =====
    "米饭": {"calcium_mg": 5, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.1, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.2, "zinc_mg": 0.4},
    "糙米饭": {"calcium_mg": 10, "trans_fat_g": 0, "saturated_fat_g": 0.3, "sugar_g": 0.4, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.5, "zinc_mg": 1.1},
    "馒头": {"calcium_mg": 18, "trans_fat_g": 0, "saturated_fat_g": 0.2, "sugar_g": 1.2, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.0, "zinc_mg": 0.7},
    "花卷": {"calcium_mg": 20, "trans_fat_g": 0, "saturated_fat_g": 0.3, "sugar_g": 1.5, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.2, "zinc_mg": 0.8},
    "面条(煮)": {"calcium_mg": 8, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.3, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.5, "zinc_mg": 0.4},
    "面条(生)": {"calcium_mg": 15, "trans_fat_g": 0, "saturated_fat_g": 0.2, "sugar_g": 0.6, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.0, "zinc_mg": 0.8},
    "挂面": {"calcium_mg": 20, "trans_fat_g": 0, "saturated_fat_g": 0.3, "sugar_g": 0.8, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.2, "zinc_mg": 1.0},
    "方便面": {"calcium_mg": 25, "trans_fat_g": 0.2, "saturated_fat_g": 5.0, "sugar_g": 1.5, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 2.0, "zinc_mg": 0.8},
    "油条": {"calcium_mg": 25, "trans_fat_g": 0.5, "saturated_fat_g": 4.5, "sugar_g": 0.5, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.2, "zinc_mg": 0.6},
    "粥(大米)": {"calcium_mg": 3, "trans_fat_g": 0, "saturated_fat_g": 0.05, "sugar_g": 0.05, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.1, "zinc_mg": 0.2},
    "粥(小米)": {"calcium_mg": 5, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.1, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.3, "zinc_mg": 0.5},
    "粥(燕麦)": {"calcium_mg": 15, "trans_fat_g": 0, "saturated_fat_g": 0.5, "sugar_g": 0.5, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.0, "zinc_mg": 1.5},
    "小米粥": {"calcium_mg": 5, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.1, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.3, "zinc_mg": 0.5},
    "玉米粥": {"calcium_mg": 5, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.2, "vitamin_a_ug": 5, "vitamin_c_mg": 0, "iron_mg": 0.4, "zinc_mg": 0.4},
    "米粉": {"calcium_mg": 10, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.2, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.5, "zinc_mg": 0.6},
    "河粉": {"calcium_mg": 8, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.1, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.4, "zinc_mg": 0.3},
    "年糕": {"calcium_mg": 12, "trans_fat_g": 0, "saturated_fat_g": 0.1, "sugar_g": 0.5, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.6, "zinc_mg": 0.5},
    "汤圆(芝麻)": {"calcium_mg": 30, "trans_fat_g": 0, "saturated_fat_g": 2.0, "sugar_g": 15.0, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.0, "zinc_mg": 0.8},
    "饺子(猪肉白菜)": {"calcium_mg": 20, "trans_fat_g": 0, "saturated_fat_g": 2.5, "sugar_g": 1.0, "vitamin_a_ug": 10, "vitamin_c_mg": 2, "iron_mg": 1.5, "zinc_mg": 1.0},
    "饺子(韭菜鸡蛋)": {"calcium_mg": 25, "trans_fat_g": 0, "saturated_fat_g": 1.8, "sugar_g": 0.8, "vitamin_a_ug": 50, "vitamin_c_mg": 3, "iron_mg": 1.8, "zinc_mg": 0.8},
    "馄饨": {"calcium_mg": 20, "trans_fat_g": 0, "saturated_fat_g": 1.5, "sugar_g": 0.5, "vitamin_a_ug": 5, "vitamin_c_mg": 1, "iron_mg": 1.2, "zinc_mg": 0.8},
    "包子(猪肉)": {"calcium_mg": 18, "trans_fat_g": 0, "saturated_fat_g": 2.5, "sugar_g": 1.0, "vitamin_a_ug": 5, "vitamin_c_mg": 1, "iron_mg": 1.5, "zinc_mg": 1.0},
    "包子(素菜)": {"calcium_mg": 25, "trans_fat_g": 0, "saturated_fat_g": 0.5, "sugar_g": 1.5, "vitamin_a_ug": 30, "vitamin_c_mg": 5, "iron_mg": 1.2, "zinc_mg": 0.6},
    "粽子(甜)": {"calcium_mg": 15, "trans_fat_g": 0, "saturated_fat_g": 0.3, "sugar_g": 8.0, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.8, "zinc_mg": 0.5},
    "粽子(鲜肉)": {"calcium_mg": 20, "trans_fat_g": 0, "saturated_fat_g": 2.0, "sugar_g": 1.0, "vitamin_a_ug": 5, "vitamin_c_mg": 1, "iron_mg": 1.5, "zinc_mg": 1.2},
    "烧饼": {"calcium_mg": 25, "trans_fat_g": 0, "saturated_fat_g": 1.0, "sugar_g": 1.0, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.5, "zinc_mg": 0.8},
    "凉皮": {"calcium_mg": 10, "trans_fat_g": 0, "saturated_fat_g": 0.2, "sugar_g": 0.5, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 0.8, "zinc_mg": 0.4},
    "八宝粥": {"calcium_mg": 20, "trans_fat_g": 0, "saturated_fat_g": 0.3, "sugar_g": 5.0, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.0, "zinc_mg": 0.8},
    "鲜面片": {"calcium_mg": 15, "trans_fat_g": 0, "saturated_fat_g": 0.2, "sugar_g": 0.5, "vitamin_a_ug": 0, "vitamin_c_mg": 0, "iron_mg": 1.0, "zinc_mg": 0.8},

    # ===== 禽肉类 (poultry) =====
    "鸡胸肉": {"calcium_mg": 5, "trans_fat_g": 0, "saturated_fat_g": 0.8, "sugar_g": 0, "vitamin_a_ug": 6, "vitamin_c_mg": 0, "iron_mg": 0.4, "zinc_mg": 0.6},
    "鸡腿肉": {"calcium_mg": 8, "trans_fat_g": 0, "saturated_fat_g": 3.5, "sugar_g": 0, "vitamin_a_ug": 15, "vitamin_c_mg": 0, "iron_mg": 0.6, "zinc_mg": 1.0},
    "鸡翅": {"calcium_mg": 12, "trans_fat_g": 0, "saturated_fat_g": 3.8, "sugar_g": 0, "vitamin_a_ug": 18, "vitamin_c_mg": 0, "iron_mg": 0.5, "zinc_mg": 0.9},
    "鸡爪": {"calcium_mg": 25, "trans_fat_g": 0, "saturated_fat_g": 3.5, "sugar_g": 0, "vitamin_a_ug": 10, "vitamin_c_mg": 0, "iron_mg": 0.6, "zinc_mg": 0.8},
    "鸡肉": {"calcium_mg": 10, "trans_fat_g": 0, "saturated_fat_g": 2.5, "sugar_g": 0, "vitamin_a_ug": 12, "vitamin_c_mg": 0, "iron_mg": 0.5, "zinc_mg": 0.9},
    "鸡肝": {"calcium_mg": 8, "trans_fat_g": 0, "saturated_fat_g": 1.5, "sugar_g": 0.5, "vitamin_a_ug": 6500, "vitamin_c_mg": 18, "iron_mg": 9.0, "zinc_mg": 2.5},
    "鸡心": {"calcium_mg": 12, "trans_fat_g": 0, "saturated_fat_g": 2.0, "sugar_g": 0.2, "vitamin_a_ug": 30, "vitamin_c_mg": 3, "iron_mg": 4.5, "zinc_mg": 2.0},
    "鸡胗": {"calcium_mg": 15, "trans_fat_g": 0, "saturated_fat_g": 1.0, "sugar_g": 0, "vitamin_a_ug": 20, "vitamin_c_mg": 2, "iron_mg": 2.5, "zinc_mg": 1.8},
    "鸭肉": {"calcium_mg": 10, "trans_fat_g": 0, "saturated_fat_g": 5.5, "sugar_g": 0, "vitamin_a_ug": 15, "vitamin_c_mg": 0, "iron_mg": 1.5, "zinc_mg": 1.5},
    "鸭腿": {"calcium_mg": 12, "trans_fat_g": 0, "saturated_fat_g": 5.0, "sugar_g": 0, "vitamin_a_ug": 18, "vitamin_c_mg": 0, "iron_mg": 1.8, "zinc_mg": 1.8},
    "鸭胸肉": {"calcium_mg": 8, "trans_fat_g": 0, "saturated_fat_g": 1.5, "sugar_g": 0, "vitamin_a_ug": 10, "vitamin_c_mg": 0, "iron_mg": 1.2, "zinc_mg": 1.2},
    "鸭肝": {"calcium_mg": 10, "trans_fat_g": 0, "saturated_fat_g": 2.0, "sugar_g": 0.5, "vitamin_a_ug": 4000, "vitamin_c_mg": 15, "iron_mg": 12.0, "zinc_mg": 3.0},
    "鸭肠": {"calcium_mg": 15, "trans_fat_g": 0, "saturated_fat_g": 3.0, "sugar_g": 0, "vitamin_a_ug": 25, "vitamin_c_mg": 2, "iron_mg": 3.0, "zinc_mg": 1.5},
    "火鸡肉": {"calcium_mg": 12, "trans_fat_g": 0, "saturated_fat_g": 0.3, "sugar_g": 0, "vitamin_a_ug": 8, "vitamin_c_mg": 0, "iron_mg": 0.8, "zinc_mg": 1.8},
    "鹌鹑": {"calcium