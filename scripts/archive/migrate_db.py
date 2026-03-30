#!/usr/bin/env python3
"""
Migrate database schema to add new columns.
"""

import argparse
import json
import os
import sqlite3
import sys


def get_db_path(username: str) -> str:
    """Get database file path for a user."""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(skill_dir, 'data')
    return os.path.join(data_dir, f"{username}.db")


def migrate_custom_foods(conn: sqlite3.Connection):
    """Add new columns to custom_foods table."""
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(custom_foods)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # Add barcode column
    if 'barcode' not in existing_columns:
        cursor.execute('ALTER TABLE custom_foods ADD COLUMN barcode TEXT')
        print("Added column: barcode")
    
    # Add brand column
    if 'brand' not in existing_columns:
        cursor.execute('ALTER TABLE custom_foods ADD COLUMN brand TEXT')
        print("Added column: brand")
    
    # Add source column
    if 'source' not in existing_columns:
        cursor.execute('ALTER TABLE custom_foods ADD COLUMN source TEXT DEFAULT "custom"')
        print("Added column: source")
    
    # Add updated_at column (SQLite doesn't support DEFAULT with ALTER)
    if 'updated_at' not in existing_columns:
        cursor.execute('ALTER TABLE custom_foods ADD COLUMN updated_at DATETIME')
        cursor.execute('UPDATE custom_foods SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL')
        print("Added column: updated_at")
    
    # Create barcode index
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_custom_foods_barcode ON custom_foods(barcode)
    ''')
    print("Created index: idx_custom_foods_barcode")
    
    conn.commit()


def migrate(username: str) -> dict:
    """Run all migrations."""
    db_path = get_db_path(username)
    
    if not os.path.exists(db_path):
        return {
            "status": "error",
            "error": "database_not_found",
            "message": f"Database not found: {db_path}"
        }
    
    conn = sqlite3.connect(db_path)
    
    try:
        migrate_custom_foods(conn)
        
        return {
            "status": "success",
            "message": "Migration completed successfully"
        }
        
    except sqlite3.Error as e:
        return {
            "status": "error",
            "error": "migration_failed",
            "message": str(e)
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='Migrate database schema')
    parser.add_argument('--user', required=True, help='Username')
    
    args = parser.parse_args()
    
    result = migrate(args.user)
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
