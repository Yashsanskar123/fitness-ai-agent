class NutritionEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def analyze(self, context=None, user_id=1):
        """
        Calculate calorie + protein targets
        """

        context = context or {}
        user = context.get("user_profile", {}) or {}

        weight = user.get("weight", 65)  # kg default
        goal = user.get("goal", "general_fitness")
        activity = user.get("activity_level", "moderate")

        # ---------------------------
        # 🔥 CALORIES
        # ---------------------------
        calories = self._calculate_calories(weight, goal, activity)

        # ---------------------------
        # 💪 PROTEIN
        # ---------------------------
        protein = self._calculate_protein(weight, goal)

        result = {
            "calories": calories,
            "protein": protein,
            "goal": goal,
            "weight": weight
        }

        print("💀 Nutrition Targets:", result)

        return result

    # ---------------------------
    # 🔥 CALORIE LOGIC
    # ---------------------------
    def _calculate_calories(self, weight, goal, activity):

        # base maintenance (very simplified)
        base = weight * 30

        # activity multiplier
        if activity == "low":
            base *= 0.9
        elif activity == "high":
            base *= 1.1

        # goal adjustment
        if goal == "fat_loss":
            return int(base - 300)
        elif goal == "muscle_gain":
            return int(base + 300)
        else:
            return int(base)

    # ---------------------------
    # 💪 PROTEIN LOGIC
    # ---------------------------
    def _calculate_protein(self, weight, goal):

        if goal == "muscle_gain":
            return round(weight * 2.0, 1)

        elif goal == "fat_loss":
            return round(weight * 1.8, 1)

        else:
            return round(weight * 1.5, 1)
        
    def generate_meal_plan(self, nutrition_targets, user_input=""):

        if not self.llm:
            return {"meals": []}

        calories = nutrition_targets.get("calories")
        protein = nutrition_targets.get("protein")

        prompt = f"""
    You are a professional fitness nutritionist.

    User goal:
    - Calories target: {calories}
    - Protein target: {protein}

    User input:
    "{user_input}"

    Task:
    Generate a FULL DAY meal plan.

    Rules:
    - High protein meals
    - Balanced carbs and fats
    - Easy to follow
    - Practical foods (home or gym friendly)
    - Divide into 4–6 meals

    Return ONLY JSON:

    {{
    "meals": [
        {{
        "name": "Breakfast",
        "food": "...",
        "calories": ...,
        "protein": ...
        }}
    ]
    }}
    """

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            response = response.strip()
            response = re.sub(r"```json|```", "", response)
            response = re.sub(r"//.*", "", response)

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                data = json.loads(match.group(0))
                print("💀 Meal Plan:", data)
                return data

        except Exception as e:
            print("⚠️ Meal LLM error:", str(e))

        return {"meals": []}