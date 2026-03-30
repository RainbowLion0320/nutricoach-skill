#!/usr/bin/env python3
"""
Migrate body_metrics table to use (user_id, date) as unique constraint.
This ensures only one weight record per day per user.
"""

import sqlite3
import os

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, 'data')


def migrate_user(username: str):
    """Migrate body_metrics table for a user."""
    db_path = os.path.join(DATA_DIR, f"{username}.db")

    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if migration already applied
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='index' AND name='idx_body_metrics_user_date_unique'
        ''')
        if cursor.fetchone():
            print(f"Migration already applied for {username}")
            return

        # Create new table with unique constraint on (user_id, date)
        cursor.execute('''
            CREATE TABLE body_metrics_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight_kg REAL NOT NULL CHECK (weight_kg > 0),
                height_cm REAL,
                body_fat_pct REAL CHECK (body_fat_pct >= 0 AND body_fat_pct <= 100),
                bmi REAL,
                recorded_date DATE NOT NULL,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'manual',
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, recorded_date)
            )
        ''')

        # Migrate data: keep only the last record of each day
        cursor.execute('''
            INSERT INTO body_metrics_new (user_id, weight_kg, height_cm, body_fat_pct, bmi, recorded_date, recorded_at, source, notes)
            SELECT
                user_id,
                weight_kg,
                height_cm,
                body_fat_pct,
                bmi,
                DATE(recorded_at) as recorded_date,
                MAX(recorded_at) as recorded_at,
                source,
                notes
            FROM body_metrics
            GROUP BY user_id, DATE(recorded_at)
        ''')

        # Drop old table and rename new one
        cursor.execute('DROP TABLE body_metrics')
        cursor.execute('ALTER TABLE body_metrics_new RENAME TO body_metrics')

        # Create indexes
        cursor.execute('CREATE INDEX idx_body_metrics_user_date ON body_metrics(user_id, recorded_date)')
        cursor.execute('CREATE INDEX idx_body_metrics_recorded ON body_metrics(recorded_at)')

        conn.commit()
        print(f"Migration completed for {username}")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed for {username}: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 migrate_body_metrics.py <username>")
        sys.exit(1)

    migrate_user(sys.argv[1])
