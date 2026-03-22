class ResponseComposer:
    def __init__(self):
        pass

    def compose(self, results):
        response = "🔥 Your Personalized Fitness Plan:\n\n"

        for res in results:
            tool = res.get("tool")
            output = res.get("output", {})

            # 🛑 Skip only if completely invalid
            if output is None:
                continue

            # 📊 INSIGHTS
            if tool == "insight_generator":
                if isinstance(output, list) and output:
                    response += "📊 Insights:\n"
                    for ins in output:
                        response += f"- {ins}\n"
                    response += "\n"

            # 🏋️ WORKOUT
            elif tool == "workout_generator":
                if output.get("exercises"):
                    response += "🏋️ Workout Plan:\n"
                    response += f"{output.get('day', 'Workout Day')}\n"

                    for ex in output.get("exercises", []):
                        name = ex.get("name", "")
                        sets = ex.get("sets", "")
                        reps = ex.get("reps", "")
                        response += f"- {name}: {sets} x {reps}\n"

                    response += "\n"

            # 🥗 DIET
            elif tool == "diet_generator":
                if output.get("meals"):
                    response += "🥗 Diet Plan:\n"
                    response += f"Calories: {output.get('total_calories', 0)}\n"
                    response += f"Protein Target: {output.get('protein_target', 0)}g\n\n"

                    for meal in output.get("meals", []):
                        response += f"{meal.get('meal')}:\n"
                        for item in meal.get("items", []):
                            response += f"  - {item}\n"
                        response += f"  Protein: {meal.get('protein')}g\n\n"

            # 😴 RECOVERY (🔥 FIXED PROPERLY)
            elif tool == "recovery_advisor":
                advice = output.get("advice")

                if advice:
                    response += "😴 Recovery Advice:\n"
                    response += f"- {advice}\n\n"

            # 🔔 NUDGE
            elif tool == "nudge_generator":
                nudges = output.get("nudges", [])

                if nudges:
                    response += "🔔 Tips:\n"
                    for n in nudges:
                        response += f"- {n}\n"
                    response += "\n"

        return response.strip()