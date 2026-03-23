class ConsistencyEngine:
    def __init__(self, memory_manager):
        self.memory = memory_manager

    def analyze(self, user_id: int):
        """
        Main entry point
        Returns behavioral intelligence
        """

        recent_workouts = self.memory.get_recent_workouts(user_id)
        streak = self.memory.get_workout_streak(user_id)
        missed = self.memory.get_missed_days(user_id)

        consistency_score = self._compute_score(recent_workouts)
        fatigue = self._estimate_fatigue(recent_workouts)
        action = self._decide_action(consistency_score, fatigue, missed)

        return {
            "consistency_score": consistency_score,
            "streak_days": streak,
            "missed_recent": missed,
            "fatigue_level": fatigue,
            "recommended_action": action
        }
    def _compute_score(self, workouts):
        if not workouts:
            return 0

        total = len(workouts)
        completed = sum(1 for w in workouts if w["completed"])

        return round(completed / total, 2)
    
    def _estimate_fatigue(self, workouts):
        high_intensity = sum(1 for w in workouts if w["intensity"] == "high")

        if high_intensity >= 4:
            return "high"
        elif high_intensity >= 2:
            return "moderate"
        return "low"
    
    def _decide_action(self, score, fatigue, missed):
        """
        This is your first version of intelligence
        Later we replace this with LLM
        """

        if score > 0.8 and fatigue == "low":
            return "increase_intensity"

        if fatigue == "high":
            return "deload"

        if missed >= 2:
            return "reduce_intensity"

        return "maintain"