class InsightEngine:

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