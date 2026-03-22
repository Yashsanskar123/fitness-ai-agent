from datetime import datetime

class NudgeEngine:

    def generate_nudges(self, context):
        nudges = []

        workouts = context.get("recent_workouts", [])
        diet = context.get("recent_diet",[])
        progress = context.get("progress", [])

        today = datetime.now().strftime("%Y-%m-%d")

        if not workouts:
            nudges.append("You havent started yet -lets begin today")

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