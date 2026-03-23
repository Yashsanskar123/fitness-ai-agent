class InsightEngine:

    def __init__(self,llm=None):
        self.llm = llm

    def generate_insights(self, context):
        insights = []

        workouts = context.get("recent_workouts", [])
        progress = context.get("progress", [])

        # 📊 Workout consistency
        if len(workouts) >= 3:
            insights.append("Good workout consistency this week.")
        else:
            insights.append("Workout consistency is low. Try to train at least 3-4 times per week.")

        # 📈 Weight trend
        if len(progress) >= 2:
            latest = progress[0]["weight"]
            prev = progress[1]["weight"]

            if latest > prev:
                insights.append(f"You gained {round(latest - prev, 1)} kg — good for muscle gain.")
            elif latest < prev:
                insights.append(f"You lost {round(prev - latest, 1)} kg — good for fat loss.")
            else:
                insights.append("No weight change detected. Consider adjusting diet or training.")

        else:
            insights.append("Not enough progress data to analyze trends.")

        return insights
    
    def generate_reasoning(self, consistency_data, action):

        # 🔁 Fallback (no LLM)
        if not self.llm:
            return self._rule_based_reasoning(consistency_data, action)

        prompt = f"""
You are a professional fitness coach.

User stats:
- Consistency Score: {consistency_data['consistency_score']}
- Workout Streak: {consistency_data['streak_days']}
- Missed Days: {consistency_data['missed_recent']}
- Fatigue Level: {consistency_data['fatigue_level']}

Decision taken: {action}

Explain in 1-2 lines WHY this decision was made.

Tone:
- Friendly
- Motivational
- Human-like

Do NOT mention AI.
"""

        try:
            response = self.llm.generate(prompt)
            return response.strip()

        except Exception as e:
            print("⚠️ Insight LLM error:", str(e))
            return self._rule_based_reasoning(consistency_data, action)

    # ---------------- RULE FALLBACK ---------------- #
    def _rule_based_reasoning(self, data, action):

        if action == "deload":
            return "Your fatigue is high and recovery is important, so we're taking it light today."

        if action == "reduce_intensity":
            return "You've missed a few workouts, so we're easing back into your routine."

        if action == "increase_intensity":
            return "You've been consistent — it's time to push harder."

        return "You're doing well — let's maintain your current pace."
