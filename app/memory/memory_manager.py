from app.db.database import Database
from datetime import datetime


class MemoryManager:
    def __init__(self):
        self.db = Database()

    # ---------------- USER ---------------- #

    def create_user(self, name, age, weight, goal, diet_type, experience_level):
        query = """
        INSERT INTO users (name, age, weight, goal, diet_type, experience_level)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.cursor.execute(query, (name, age, weight, goal, diet_type, experience_level))
        self.db.conn.commit()

        return self.db.cursor.lastrowid

    def get_user(self, user_id=1):
        query = "SELECT * FROM users WHERE id = ?"
        self.db.cursor.execute(query, (user_id,))
        row = self.db.cursor.fetchone()

        return dict(row) if row else None

    # ---------------- WORKOUT ---------------- #

    def log_workout(self, user_id, workout_done, duration, notes=""):
        query = """
        INSERT INTO workout_logs (user_id, date, workout_done, duration, notes)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.cursor.execute(query, (
            user_id,
            datetime.now().strftime("%Y-%m-%d"),
            workout_done,
            duration,
            notes
        ))
        self.db.conn.commit()

    def get_workout_history(self, user_id=1, limit=5):
        query = """
        SELECT * FROM workout_logs
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
        """
        self.db.cursor.execute(query, (user_id, limit))
        rows = self.db.cursor.fetchall()

        return [dict(row) for row in rows]

    # ---------------- DIET ---------------- #

    def log_diet(self, user_id, meals, protein_intake, calories):
        query = """
        INSERT INTO diet_logs (user_id, date, meals, protein_intake, calories)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.cursor.execute(query, (
            user_id,
            datetime.now().strftime("%Y-%m-%d"),
            meals,
            protein_intake,
            calories
        ))
        self.db.conn.commit()

    def get_diet_history(self, user_id=1, limit=5):
        query = """
        SELECT * FROM diet_logs
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
        """
        self.db.cursor.execute(query, (user_id, limit))
        rows = self.db.cursor.fetchall()

        return [dict(row) for row in rows]

    # ---------------- PROGRESS ---------------- #

    def log_progress(self, user_id, weight, body_fat=None, strength_notes=""):
        query = """
        INSERT INTO progress_logs (user_id, date, weight, body_fat, strength_notes)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.cursor.execute(query, (
            user_id,
            datetime.now().strftime("%Y-%m-%d"),
            weight,
            body_fat,
            strength_notes
        ))
        self.db.conn.commit()

    def get_progress_history(self, user_id=1, limit=5):
        query = """
        SELECT * FROM progress_logs
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
        """
        self.db.cursor.execute(query, (user_id, limit))
        rows = self.db.cursor.fetchall()

        return [dict(row) for row in rows]

    # ---------------- CONTEXT BUILDER (VERY IMPORTANT) ---------------- #

    def build_user_context(self, user_id=1):
        """
        This is what we will send to LLM later
        """

        user = self.get_user(user_id)
        workouts = self.get_workout_history(user_id)
        diet = self.get_diet_history(user_id)
        progress = self.get_progress_history(user_id)

        context = {
            "user_profile": user,
            "recent_workouts": workouts,
            "recent_diet": diet,
            "progress": progress
        }

        return context 
    
    def save_workout(self, user_id, workout, duration=60, notes=""):
        try:
            from app.db.database import Database

            db = Database()

            db.cursor.execute("""
                INSERT INTO workout_logs (user_id, date, workout_done, duration, notes)
                VALUES (?, DATE('now'), ?, ?, ?)
            """, (user_id, workout, duration, notes))

            db.conn.commit()
            db.close()

            print("💾 Workout saved")

        except Exception as e:
            print("❌ SAVE WORKOUT ERROR:", str(e))


    def save_diet(self, user_id, meals, protein, calories):
        try:
            from app.db.database import Database

            db = Database()

            db.cursor.execute("""
                INSERT INTO diet_logs (user_id, date, meals, protein_intake, calories)
                VALUES (?, DATE('now'), ?, ?, ?)
            """, (user_id, meals, protein, calories))

            db.conn.commit()
            db.close()

            print("💾 Diet saved")

        except Exception as e:
            print("❌ SAVE DIET ERROR:", str(e))