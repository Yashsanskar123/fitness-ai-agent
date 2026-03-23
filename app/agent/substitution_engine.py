class SubstitutionEngine:

    def __init__(self, llm=None):
        self.llm = llm

    def suggest_substitution(self, exercise, injuries):
        """
        Suggest safe alternative exercise based on injuries
        """

        if not self.llm or not injuries:
            return {
                "original": exercise,
                "replacement": exercise,
                "reason": "no substitution needed"
            }

        prompt = f"""
You are an expert fitness coach.

Task:
Suggest a SAFE alternative exercise.

Given:
- Exercise: {exercise}
- User Injuries: {injuries}

Rules:
- Avoid movements that stress injured areas
- Keep same muscle group
- Prefer safer variations
- If no good alternative → return "skip"

Return ONLY JSON:

{{
  "original": "...",
  "replacement": "...",
  "reason": "..."
}}
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            response = response.strip()
            response = re.sub(r"```json|```", "", response)

            # 🔥 remove comments if any
            response = re.sub(r"//.*", "", response)

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                json_str = match.group(0)

                try:
                    data = json.loads(json_str)

                    replacement = data.get("replacement", exercise)

                    # 🔥 fallback safety
                    if not replacement or replacement.lower() == "skip":
                        return {
                            "original": exercise,
                            "replacement": "skip",
                            "reason": "no safe alternative found"
                        }

                    return data

                except:
                    print("⚠️ Substitution JSON parse failed:", json_str)

        except Exception as e:
            print("❌ Substitution error:", str(e))

        # 🔁 fallback (no crash ever)
        return {
            "original": exercise,
            "replacement": exercise,
            "reason": "fallback - no substitution"
        }

    def apply_substitutions(self, workout_plan, injuries):
        """
        Apply substitution to full workout plan
        """

        if not workout_plan or "exercises" not in workout_plan:
            return workout_plan
        if not injuries:
            return workout_plan
        
        updated_exercises = []

        for ex in workout_plan.get("exercises", []):
            original_name = ex.get("name")

            result = self.suggest_substitution(original_name, injuries)

            replacement = result.get("replacement", original_name)

            if replacement == "skip":
                continue

            ex["name"] = replacement

            updated_exercises.append(ex)

        workout_plan["exercises"] = updated_exercises
        return workout_plan
