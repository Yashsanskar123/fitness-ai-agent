class MultiDayEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def generate_plan(self, context, user_id=1):
        """
        Generate a multi-day workout structure (NOT exercises)
        """

        user_profile = context.get("user_profile", {}) or {}
        injuries = context.get("injuries", []) or []

        goal = user_profile.get("goal", "general")
        experience = user_profile.get("experience", "beginner")

        # ---------------------------
        # 🤖 LLM PLAN GENERATION
        # ---------------------------
        if self.llm:
            return self._llm_generate(goal, experience, injuries)

        # ---------------------------
        # 🔁 FALLBACK
        # ---------------------------
        return self._fallback_plan(goal)

    # ---------------------------
    # 🤖 LLM GENERATION
    # ---------------------------
    def _llm_generate(self, goal, experience, injuries):

        prompt = f"""
You are an expert fitness coach.

User:
- Goal: {goal}
- Experience: {experience}
- Injuries: {injuries}

Create a structured 5–7 day workout schedule.

Rules:
- Include rest days
- Match experience level
- Consider injuries (avoid overloading injured areas)
- Keep it realistic

IMPORTANT:
- DO NOT include exercises
- ONLY return focus for each day

Return ONLY JSON:

{{
  "plan_duration": "X days",
  "schedule": [
    {{"day": 1, "focus": "..."}},
    {{"day": 2, "focus": "..."}}
  ]
}}

Focus examples:
chest, back, legs, shoulders, arms, full body, rest
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

                print("📅 Multi-day plan:", data)

                return data

        except Exception as e:
            print("⚠️ MultiDay LLM error:", str(e))

        return self._fallback_plan(goal)

    # ---------------------------
    # 🔁 FALLBACK PLAN
    # ---------------------------
    def _fallback_plan(self, goal):

        # minimal safe fallback (NO HARDCODED COMPLEX LOGIC)
        return {
            "plan_duration": "3 days",
            "schedule": [
                {"day": 1, "focus": "full body"},
                {"day": 2, "focus": "rest"},
                {"day": 3, "focus": "full body"}
            ]
        }