class MultiDayEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def generate_plan(self, context, user_id=1):
        """
        Generate a multi-day workout structure (NOT exercises)
        """

        context = context or {}
        user_profile = context.get("user_profile", {}) or {}
        injuries = context.get("injuries", []) or []

        goal = user_profile.get("goal", "general")
        experience = user_profile.get("experience", "beginner")

        # ---------------------------
        # 📊 MEMORY (NEW)
        # ---------------------------
        progress = []
        if self.memory:
            try:
                progress = self.memory.get_progress_history(user_id)
            except Exception as e:
                print("⚠️ Memory read failed:", str(e))
                progress = []

        # ---------------------------
        # 🤖 LLM PLAN GENERATION
        # ---------------------------
        if self.llm:
            return self._llm_generate(goal, experience, injuries, progress)

        # ---------------------------
        # 🔁 FALLBACK
        # ---------------------------
        return self._fallback_plan(goal)

    # ---------------------------
    # 🤖 LLM GENERATION
    # ---------------------------
    def _llm_generate(self, goal, experience, injuries, progress):

        prompt = f"""
You are an expert AI fitness planner.

User Profile:
- Goal: {goal}
- Experience: {experience}
- Injuries: {injuries}
- Progress History: {progress}

Task:
Generate a structured weekly workout plan (5–7 days).

Guidelines:
- Balance muscle groups across the week
- Avoid training same muscles on consecutive days
- Include at least 1–2 rest days
- Adjust difficulty based on experience level
- Avoid stressing injured areas
- Keep it realistic and sustainable

STRICT RULES:
- DO NOT include exercises
- ONLY provide daily focus
- Keep output clean JSON only

Return ONLY JSON:
{{
  "plan_duration": "X days",
  "schedule": [
    {{"day": 1, "focus": "..."}},
    {{"day": 2, "focus": "..."}}
  ]
}}
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            # ---------------------------
            # 🧹 CLEAN RESPONSE
            # ---------------------------
            response = response.strip()
            response = re.sub(r"```json|```", "", response)
            response = re.sub(r"//.*", "", response)

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if not match:
                raise ValueError("No JSON found in LLM response")

            data = json.loads(match.group(0))

            # ---------------------------
            # ✅ VALIDATION (NEW)
            # ---------------------------
            if "schedule" not in data or not isinstance(data["schedule"], list):
                raise ValueError("Invalid schedule format")

            # Ensure at least 1 rest day
            has_rest = any(
                "rest" in day.get("focus", "").lower()
                for day in data["schedule"]
            )

            if not has_rest:
                data["schedule"].append({
                    "day": len(data["schedule"]) + 1,
                    "focus": "rest"
                })

            # Ensure plan_duration exists
            if "plan_duration" not in data:
                data["plan_duration"] = f"{len(data['schedule'])} days"

            print("📅 Multi-day plan:", data)

            return data

        except Exception as e:
            print("⚠️ MultiDay LLM error:", str(e))

        # fallback if anything fails
        return self._fallback_plan(goal)

    # ---------------------------
    # 🔁 FALLBACK PLAN
    # ---------------------------
    def _fallback_plan(self, goal):

        # minimal safe fallback (NO COMPLEX HARDCODE)
        return {
            "plan_duration": "3 days",
            "schedule": [
                {"day": 1, "focus": "full body"},
                {"day": 2, "focus": "rest"},
                {"day": 3, "focus": "full body"}
            ]
        }