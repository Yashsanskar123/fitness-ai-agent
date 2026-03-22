class GoalEngine:
    def __init__(self):
        pass

    def generate_plan(self, context):
        user = context.get("user_profile", {})
        goal = user.get("goal", "general")

        if goal == "muscle_gain":
            return self.muscle_gain_plan()

        elif goal == "fat_loss":
            return self.fat_loss_plan()

        else:
            return self.general_plan()

    # ---------------- MUSCLE GAIN ---------------- #

    def muscle_gain_plan(self):
        return {
            "goal": "muscle_gain",
            "strategy": [
                "Train 4-5 times per week",
                "Focus on progressive overload",
                "Maintain high protein diet",
                "Ensure proper recovery"
            ],
            "weekly_plan": {
                "Day 1": "Chest",
                "Day 2": "Back",
                "Day 3": "Rest",
                "Day 4": "Legs",
                "Day 5": "Shoulders",
                "Day 6": "Arms",
                "Day 7": "Rest"
            }
        }

    # ---------------- FAT LOSS ---------------- #

    def fat_loss_plan(self):
        return {
            "goal": "fat_loss",
            "strategy": [
                "Train 4-6 times per week",
                "Add cardio sessions",
                "Maintain calorie deficit",
                "High protein intake"
            ],
            "weekly_plan": {
                "Day 1": "Full Body",
                "Day 2": "Cardio",
                "Day 3": "Upper Body",
                "Day 4": "Rest",
                "Day 5": "Lower Body",
                "Day 6": "Cardio",
                "Day 7": "Rest"
            }
        }

    # ---------------- GENERAL ---------------- #

    def general_plan(self):
        return {
            "goal": "general_fitness",
            "strategy": [
                "Stay active daily",
                "Mix strength + cardio",
                "Eat balanced diet"
            ],
            "weekly_plan": {}
        }
    
    def get_today_focus(self, context):
        plan = self.generate_plan(context)

        weekly_plan = plan.get("weekly_plan", {})

        from datetime import datetime
        day_index = datetime.now().weekday()

        day_map = {
        0: "Day 1",
        1: "Day 2",
        2: "Day 3",
        3: "Day 4",
        4: "Day 5",
        5: "Day 6",
        6: "Day 7",
    }

        today = day_map.get(day_index)
        focus = weekly_plan.get(today, "full body")
        return focus.lower()
    
    def get_next_focus(self,context):
        workouts  = context.get("recent_workouts", [])
        workouts = sorted(
            workouts,
            key = lambda x: (x.get("date", ""), x.get("id",0)),
            reverse = True
        )
        print("Sorted workouts:", [w.get("workout_done")for w in workouts[:5]])

        if not workouts:
            return "full body"
        
        recent = [w.get("workout_done","").lower() for w in workouts[1:4]]
        def detect_body_part(text):
            if "chest" in text:
                return "chest"
            elif "back" in text:
                return "back"
            elif "leg" in text:
                return "legs"
            elif "shoulder" in text:
                return "shoulders"
            elif "arm" in text or "bicep" in text or "tricep" in text:
                return "arms"
            else:
                return None
        detected = [detect_body_part(w) for w in recent if w]

        detected = [d for d in detected if d]

        print("Raw Workouts:", [w["workout_done"] for w in workouts])

        if not detected:
            return "full body"
        
        possible = ["chest", "back", "legs","shoulders", "arms"]

        next_options = [m for m in possible if m not in detected]

        if not next_options:
            next_options = [m for m in possible if m!= detected[0]]

        return next_options[0]
