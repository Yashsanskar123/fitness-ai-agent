class FormSafetyEngine:

    def __init__(self, llm=None):
        self.llm = llm

    def generate_tips(self, exercise, injuries=None, phase="foundation"):
        """
        Generate form and safety tips for an exercise
        """

        injuries = injuries or []

        if not self.llm:
            return {
                "exercise": exercise,
                "tips": [],
                "safety": []
            }

        prompt = f"""
You are an expert fitness coach.

Exercise:
{exercise}

User Injuries:
{injuries}

User Training Phase:
{phase}

Task:
Provide form and safety advice.

Rules:
- Give 2-3 form tips
- Give 1-2 safety warnings
- Adjust advice based on injuries
- Adjust advice based on training phase
- Keep tips short and practical

Return ONLY JSON:

{{
  "exercise": "...",
  "tips": ["...", "..."],
  "safety": ["...", "..."]
}}
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            # 🔧 CLEAN RESPONSE
            response = response.strip()
            response = re.sub(r"```json|```", "", response)
            response = re.sub(r"//.*", "", response)

            # 🔍 EXTRACT JSON
            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                json_str = match.group(0)

                try:
                    data = json.loads(json_str)

                    # 🔥 SAFETY CLEANUP
                    tips = data.get("tips", [])
                    safety = data.get("safety", [])

                    if not isinstance(tips, list):
                        tips = []
                    if not isinstance(safety, list):
                        safety = []

                    return {
                        "exercise": exercise,
                        "tips": tips[:3],     # limit
                        "safety": safety[:2]  # limit
                    }

                except:
                    print("⚠️ FormSafety JSON parse failed:", json_str)

        except Exception as e:
            print("❌ FormSafety error:", str(e))

        # 🔁 fallback (never break system)
        return {
            "exercise": exercise,
            "tips": ["Focus on controlled movement"],
            "safety": ["Avoid pain during execution"]
        }
    

    def apply_form_safety(self, workout_plan, injuries=None, phase="foundation"):
        """
        Apply form + safety tips to full workout
        """

        if not workout_plan or "exercises" not in workout_plan:
            return workout_plan

        injuries = injuries or []

        updated_exercises = []

        for ex in workout_plan.get("exercises", []):
            name = ex.get("name")

            tips_data = self.generate_tips(
                exercise=name,
                injuries=injuries,
                phase=phase
            )

            ex["tips"] = tips_data.get("tips", [])
            ex["safety"] = tips_data.get("safety", [])

            updated_exercises.append(ex)

        workout_plan["exercises"] = updated_exercises

        return workout_plan