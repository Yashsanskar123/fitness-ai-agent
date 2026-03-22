from datetime import datetime


class AdaptiveEngine:

    def analyze(self, context):
        insights = []

        workouts = context.get("recent_workouts", [])
        progress = context.get("progress", [])

        # 🧠 1. Missed workout detection
        if len(workouts) < 2:
            insights.append("low_activity")

        # 🧠 2. Progress analysis
        if len(progress) >= 2:
            latest = progress[0]["weight"]
            prev = progress[1]["weight"]

            if latest > prev:
                insights.append("weight_gain")
            elif latest < prev:
                insights.append("weight_loss")
            else:
                insights.append("no_change")

        return insights

    def modify_workout(self, workout_plan, insights):

        if "low_activity" in insights:
            workout_plan["note"] = "You’ve been less active. Starting light today."

            for ex in workout_plan.get("exercises", []):
                ex["sets"] = max(2, ex["sets"] - 1)

        if "weight_gain" in insights:
            workout_plan["note"] = "Progressing well. Increasing intensity."

            for ex in workout_plan.get("exercises", []):
                ex["sets"] += 1

        return workout_plan

    def generate_coaching_tip(self, insights):

        if "low_activity" in insights:
            return "Try to stay consistent. Even 30 mins daily helps."

        if "weight_gain" in insights:
            return "Great progress! Keep pushing."

        if "no_change" in insights:
            return "We need to tweak your routine for better results."

        return "Stay consistent and focused."
    
    def adapt_plan(self, plan, context, user_input):
        if not plan:
            return plan

        user_input = user_input.lower()
        workouts = context.get("recent_workouts", [])

        last_workout = ""
        if workouts:
            last_workout = workouts[0].get("workout_done", "").lower()

        adapted_plan = []

        for step in plan:
            tool = step.get("tool")
            args = step.get("args", {})

            # 🔥 Only modify workout step
            if tool == "workout_generator":

                focus = args.get("focus", "full body")
                intensity = args.get("intensity", "medium")

                # ---------------------------
                # 🧠 Rule 1: Avoid repetition
                # ---------------------------
                if "chest" in last_workout and focus == "chest":
                    focus = "back"

                elif "back" in last_workout and focus == "back":
                    focus = "legs"

                elif "legs" in last_workout and focus == "legs":
                    focus = "upper body"

                # ---------------------------
                # 🧠 Rule 2: Recovery override
                # ---------------------------
                if "sore" in user_input or "pain" in user_input:
                    intensity = "low"
                    focus = "full body"

                # ---------------------------
                # 🧠 Rule 3: No activity
                # ---------------------------
                if len(workouts) == 0:
                    intensity = "low"
                    focus = "full body"

                # APPLY BACK
                step["args"] = {
                    "focus": focus,
                    "intensity": intensity
                }

            adapted_plan.append(step)

        return adapted_plan