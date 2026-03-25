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
        
    def _clean_llm_json(self, response: str):
        import json
        import re

        try:
            # remove markdown
            response = re.sub(r"```json|```", "", response)

            # remove comments
            response = re.sub(r"//.*", "", response)

            # remove units (30g → 30)
            response = re.sub(r'(\d+)\s*g', r'\1', response)

            # remove trailing commas
            response = re.sub(r",\s*}", "}", response)
            response = re.sub(r",\s*]", "]", response)

            # extract JSON
            match = re.search(r"\{.*\}", response, re.DOTALL)

            if not match:
                raise ValueError("No JSON found")

            json_str = match.group(0)

            data = json.loads(json_str)

            return data

        except Exception as e:
            print("💀 JSON CLEAN FAILED:", str(e))
            return {}        

        
    def generate_meal_plan(self, nutrition_targets, user_input=""):

        if not self.llm:
            return {"error": "LLM not available", "meals": []}

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

    STRICT RULES:
    - ONLY return valid JSON
    - NO markdown (no ```json)
    - NO explanation
    - NO text outside JSON
    - Numbers must be integers (NO 30g, only 30)
    
    Format:
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
            cleaned = self._clean_llm_json(response)

            if not cleaned.get("meals"):
                raise ValueError("empty meals after parsing")
            print("Cleaned meal plan", cleaned)
            return cleaned
        except Exception as e:
            print("Meal LLM Error:", str(e))

            return {
                "error":"Meal generation failed",
                "raw_output": response if 'response' in locals() else "",
                "meals": []
            }

            