class ProgressionEngine:

    def __init__(self, memory_manager):
        self.memory = memory_manager

    def analyze(self, user_id=1):
        """
        Main method → returns progression signals
        """

        progress_data = self.memory.get_progress_history(user_id) or []
        workout_data = self.memory.get_recent_workouts(user_id) or []

        weight_trend = self._analyze_weight_trend(progress_data)
        workout_trend = self._analyze_workout_frequency(workout_data)
        intensity_trend = self._analyze_intensity_trend(workout_data)

        # 🔥 Handle low data case
        if len(progress_data) < 3:
            print("⚠️ Not enough data for strong progression signal")

            return {
                "weight_trend": "unknown",
                "workout_trend": workout_trend,
                "intensity_trend": intensity_trend,
                "progress_status": "insufficient_data"
            }

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

        try:
            weights = [p.get("weight", 0) for p in progress[:3] if p.get("weight")]

            if len(weights) < 2:
                return "unknown"

            # 🔥 smoother trend (average difference)
            avg_prev = sum(weights[1:]) / (len(weights) - 1)
            latest = weights[0]

            diff = latest - avg_prev

            if diff > 0.3:
                return "increasing"
            elif diff < -0.3:
                return "decreasing"
            else:
                return "stagnant"

        except Exception as e:
            print("⚠️ Weight trend error:", str(e))
            return "unknown"

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

        try:
            high = sum(
                1 for w in workouts
                if w.get("intensity", "moderate") == "high"
            )

            total = len(workouts)
            ratio = high / total if total > 0 else 0

            if ratio > 0.6:
                return "high"
            elif ratio > 0.3:
                return "moderate"
            return "low"

        except Exception as e:
            print("⚠️ Intensity trend error:", str(e))
            return "unknown"

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

    # ---------------- PROGRESSION DECISION ---------------- #

    def generate_progression(self, progress_data):

        status = progress_data.get("progress_status")

        if status == "progressing":
            return {
                "action": "increase",
                "message": "Increase weight by 2.5–5% or add 1–2 reps"
            }

        elif status == "plateau":
            return {
                "action": "modify",
                "message": "Change exercise variation or increase intensity"
            }

        elif status == "inconsistent":
            return {
                "action": "reduce",
                "message": "Focus on consistency before increasing intensity"
            }

        elif status == "cutting":
            return {
                "action": "maintain",
                "message": "Maintain weight, increase reps slightly"
            }

        elif status == "insufficient_data":
            return {
                "action": "maintain",
                "message": "Collect more data before progression"
            }

        return {
            "action": "maintain",
            "message": "Maintain current plan"
        }

    # ---------------- APPLY PROGRESSION ---------------- #

    def apply_progression(self, workout_plan, progress_data):
        """
        Apply progression decision to workout
        """

        decision = self.generate_progression(progress_data)

        for ex in workout_plan.get("exercises", []):
            ex["progression"] = decision["message"]

        return workout_plan

    # ---------------- DELOAD DETECTION ---------------- #

    def check_deload(self, progress_data):
        """
        Detect overtraining → suggest deload
        """

        status = progress_data.get("progress_status")
        intensity = progress_data.get("intensity_trend")

        if status == "plateau" and intensity == "high":
            return True

        return False