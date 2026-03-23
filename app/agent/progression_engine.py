class ProgressionEngine:

    def __init__(self, memory_manager):
        self.memory = memory_manager

    def analyze(self, user_id=1):
        """
        Main method → returns progression signals
        """

        progress_data = self.memory.get_progress_history(user_id)
        workout_data = self.memory.get_recent_workouts(user_id)

        weight_trend = self._analyze_weight_trend(progress_data)
        workout_trend = self._analyze_workout_frequency(workout_data)
        intensity_trend = self._analyze_intensity_trend(workout_data)

        progress_status = self._summarize_progress(
            weight_trend,
            workout_trend,
            intensity_trend
        )

        return {
            "weight_trend": weight_trend,
            "workout_trend": workout_trend,
            "intensity_trend": intensity_trend,
            "progress_status": progress_status
        }

    # ---------------- WEIGHT TREND ---------------- #

    def _analyze_weight_trend(self, progress):

        if len(progress) < 2:
            return "unknown"

        latest = progress[0]["weight"]
        prev = progress[1]["weight"]

        if latest > prev:
            return "increasing"
        elif latest < prev:
            return "decreasing"
        else:
            return "stagnant"

    # ---------------- WORKOUT FREQUENCY ---------------- #

    def _analyze_workout_frequency(self, workouts):

        if not workouts:
            return "low"

        count = len(workouts)

        if count >= 5:
            return "high"
        elif count >= 3:
            return "moderate"
        return "low"

    # ---------------- INTENSITY TREND ---------------- #

    def _analyze_intensity_trend(self, workouts):

        if not workouts:
            return "unknown"

        high = sum(1 for w in workouts if w.get("intensity") == "high")
        total = len(workouts)

        ratio = high / total

        if ratio > 0.6:
            return "high"
        elif ratio > 0.3:
            return "moderate"
        return "low"

    # ---------------- FINAL SUMMARY ---------------- #

    def _summarize_progress(self, weight, workout, intensity):

        if workout == "low":
            return "inconsistent"

        if weight == "increasing" and intensity != "low":
            return "progressing"

        if weight == "stagnant":
            return "plateau"

        if weight == "decreasing":
            return "cutting"

        return "stable"