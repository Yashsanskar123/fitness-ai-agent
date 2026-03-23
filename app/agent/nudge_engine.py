from datetime import datetime, timedelta


class NudgeEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    # ---------------- EXISTING LOGIC (UNCHANGED) ---------------- #

    def generate_nudges(self, context):
        nudges = []

        workouts = context.get("recent_workouts", [])
        diet = context.get("recent_diet", [])
        progress = context.get("progress", [])

        today = datetime.now().strftime("%Y-%m-%d")

        if not workouts:
            nudges.append("You havent started yet - lets begin today")

        else:
            last_workout = workouts[0]["date"]

            if last_workout != today:
                nudges.append("You havent worked out today. lets stay consistent!")

        if diet:
            last_diet = diet[0]

            if last_diet.get("protein_intake", 0) < 80:
                nudges.append("Your protein intake is low. Try increasing it today.")
        else:
            nudges.append("No diet logged today - track your meals to stay on target")

        if progress:
            nudges.append("Keep going! you are making progress")

        return {
            "nudges": nudges
        }

    # ---------------- NEW: SMART NUDGE (BEHAVIOR BASED) ---------------- #

    def generate_smart_nudge(self, user_id=1):

        if not self.memory:
            return None

        workouts = self.memory.get_recent_workouts(user_id)

        if not workouts:
            return "Let’s start your fitness journey today 💪"

        last_date_str = workouts[0]["date"]
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        today = datetime.now().date()

        days_gap = (today - last_date).days

        if days_gap == 0:
            return None

        # ---------------------------
        # 🤖 LLM-based nudge
        # ---------------------------
        if self.llm:
            return self._llm_nudge(days_gap)

        # ---------------------------
        # 🔁 fallback
        # ---------------------------
        return self._rule_based_nudge(days_gap)

    # ---------------- LLM NUDGE ---------------- #

    def _llm_nudge(self, days_gap):

        prompt = f"""
You are a fitness coach.

User has not worked out for {days_gap} days.

Generate a short motivational nudge.

Tone:
- Friendly
- Motivational
- Slightly pushy if needed

Do not mention AI.
"""

        try:
            response = self.llm.generate(prompt)
            return response.strip()

        except Exception as e:
            print("⚠️ LLM Nudge Error:", str(e))
            return self._rule_based_nudge(days_gap)

    # ---------------- RULE BASED ---------------- #

    def _rule_based_nudge(self, days_gap):

        if days_gap == 1:
            return "You’re doing great — let’s keep the streak alive today 💪"

        elif days_gap <= 3:
            return f"You’ve missed {days_gap} days — let’s get back on track 🔥"

        else:
            return f"It’s been {days_gap} days! Time to restart and come back stronger 💀"