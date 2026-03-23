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
        injuries = self.get_user_injuries(user_id)

        context = {
            "user_profile": user,
            "recent_workouts": workouts,
            "recent_diet": diet,
            "progress": progress,
            "injuries": injuries
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

    def get_recent_workouts(self, user_id: int, days: int = 7):
        query = """
        SELECT date, workout_done, duration, notes
        FROM workout_logs
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
        """

        self.db.cursor.execute(query, (user_id, days))
        rows = self.db.cursor.fetchall()

        workouts = []
        for row in rows:
            duration = row["duration"]

            # 🔥 Derive intensity from duration
            if duration >= 60:
                intensity = "high"
            elif duration >= 30:
                intensity = "moderate"
            else:
                intensity = "low"

            workouts.append({
                "date": row["date"],
                "workout_type": row["workout_done"],
                "duration": duration,
                "intensity": intensity,
                "completed": True  # since logged = completed
            })

        return workouts
    
    def get_workout_streak(self, user_id: int):
        query = """
        SELECT date
        FROM workout_logs
        WHERE user_id = ?
        ORDER BY date DESC
        """

        self.db.cursor.execute(query, (user_id,))
        rows = self.db.cursor.fetchall()

        if not rows:
            return 0

        from datetime import datetime, timedelta

        streak = 0
        current_date = datetime.now().date()

        for row in rows:
            workout_date = datetime.strptime(row["date"], "%Y-%m-%d").date()

            if workout_date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break

        return streak
    
    def get_missed_days(self, user_id: int, days: int = 7):
        query = """
        SELECT date
        FROM workout_logs
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
        """

        self.db.cursor.execute(query, (user_id,days))
        rows = self.db.cursor.fetchall()

        logged_dates = set(row["date"] for row in rows)

        from datetime import datetime, timedelta

        today = datetime.now().date()
        missed = 0

        for i in range(days):
            check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")

            if check_date not in logged_dates:
                missed += 1

        return missed
    
    def save_learning(self, user_id, decision, consistency, progression, outcome):
        """
        Store one learning experience
        """

        try:
            import json
            from datetime import datetime

            query="""
            INSERT INTO learning_logs (
                user_id,
                date,
                decision,
                consistency_data,
                progression_data,
                outcome
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """     
            self.db.cursor.execute(query, (
                user_id,
                datetime.now().strftime("%Y-%m-%d"),
                decision,
                json.dumps(consistency),
                json.dumps(progression),
                json.dumps(outcome)
            ))

            self.db.conn.commit()

            print(" Learning Saved")
        except Exception as e:
            print(" Save Learning Error:", str(e))

    def get_recent_learning(self, user_id=1, limit=5):
        """
        Fetch recent learning experiences
        """

        try:
            import json

            query = """
            SELECT decision, consistency_data, progression_data, outcome
            FROM learning_logs
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT ?
            """

            self.db.cursor.execute(query, (user_id, limit))
            rows = self.db.cursor.fetchall()

            results = []

            for row in rows:
                results.append({
                    "decision": row["decision"],
                    "consistency": json.loads(row["consistency_data"]),
                    "progression": json.loads(row["progression_data"]),
                    "outcome": json.loads(row["outcome"])
                })

            return results

        except Exception as e:
            print("❌ FETCH LEARNING ERROR:", str(e))
            return []
        
    def save_injury(self, user_id, injury_type, severity="moderate", notes=""):
        """
        Store user injury info
        """

        try:
            query = """
            INSERT INTO user_injuries (user_id, injury_type, severity, notes)
            VALUES (?, ?, ?, ?)
            """

            self.db.cursor.execute(query, (
                user_id,
                injury_type.lower(),
                severity.lower(),
                notes
            ))

            self.db.conn.commit()

            print("🩹 Injury saved")

        except Exception as e:
            print("❌ SAVE INJURY ERROR:", str(e))

    def get_user_injuries(self, user_id=1):
        """
        Fetch all user injuries
        """

        try:
            query = """
            SELECT injury_type, severity, notes
            FROM user_injuries
            WHERE user_id = ?
            ORDER BY created_at DESC
            """

            self.db.cursor.execute(query, (user_id,))
            rows = self.db.cursor.fetchall()

            injuries = []

            for row in rows:
                injuries.append({
                    "injury_type": row["injury_type"],
                    "severity": row["severity"],
                    "notes": row["notes"]
                })

            return injuries

        except Exception as e:
            print("❌ FETCH INJURY ERROR:", str(e))
            return []