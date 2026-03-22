import sqlite3
from pathlib import Path

# Database file path
DB_PATH = Path("fitness.db")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Create all required tables"""

        # USERS TABLE
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            weight REAL,
            goal TEXT,
            diet_type TEXT,
            experience_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # WORKOUT LOGS
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            workout_done TEXT,
            duration INTEGER,
            notes TEXT
        )
        """)

        # DIET LOGS
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            meals TEXT,
            protein_intake REAL,
            calories INTEGER
        )
        """)

        # PROGRESS LOGS
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            body_fat REAL,
            strength_notes TEXT
        )
        """)

        self.conn.commit()

    def close(self):
        self.conn.close()


# Initialize DB (auto-run when file is used)
if __name__ == "__main__":
    db = Database()
    db.create_tables()
    print("✅ Database & tables created successfully!")
    db.close()