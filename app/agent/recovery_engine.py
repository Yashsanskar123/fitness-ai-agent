class RecoveryEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def analyze(self, user_id=1, context=None, consistency=None, performance=None, user_input=""):
        """
        Decide whether recovery is needed
        """

        context = context or {}
        consistency = consistency or {}
        performance = performance or {}

        # ---------------------------
        # 🧠 Rule-based signals
        # ---------------------------
        fatigue_flag = False

        streak = consistency.get("streak_days", 0)
        fatigue_level = consistency.get("fatigue_level", "low")
        missed = consistency.get("missed_recent", 0)

        perf_fatigue = performance.get("fatigue_level", "low")
        perf_status = performance.get("performance_status", "unknown")

        user_input = user_input.lower()

        # 💀 Basic signals
        if streak >= 5:
            fatigue_flag = True

        if fatigue_level == "high" or perf_fatigue == "high":
            fatigue_flag = True

        if "tired" in user_input or "sore" in user_input or "low energy" in user_input:
            fatigue_flag = True

        # ---------------------------
        # 🤖 LLM decision (if available)
        # ---------------------------
        if self.llm:
            return self._llm_decide(
                consistency,
                performance,
                context,
                user_input
            )

        # ---------------------------
        # 🔁 Fallback logic
        # ---------------------------
        if fatigue_flag:
            return {
                "recovery_needed": True,
                "recovery_type": "light",
                "reason": "User showing fatigue signals"
            }

        return {
            "recovery_needed": False,
            "recovery_type": "none",
            "reason": "User is in good condition"
        }

    # ---------------------------
    # 🤖 LLM DECISION
    # ---------------------------
    def _llm_decide(self, consistency, performance, context, user_input):

        prompt = f"""
You are an expert fitness recovery coach.

User data:

Consistency:
- Streak: {consistency.get("streak_days")}
- Missed Days: {consistency.get("missed_recent")}
- Fatigue: {consistency.get("fatigue_level")}

Performance:
- Status: {performance.get("performance_status")}
- Fatigue: {performance.get("fatigue_level")}

Recent workouts:
{context.get("recent_workouts", [])}

User input:
"{user_input}"

Decide:
- Does the user need recovery?
- What type?

Recovery types:
rest
light
deload

Return ONLY JSON:

{{
  "recovery_needed": true/false,
  "recovery_type": "rest/light/deload",
  "reason": "short explanation"
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
                print("💀 Recovery Decision:", data)
                return data

        except Exception as e:
            print("⚠️ Recovery LLM error:", str(e))

        # fallback if LLM fails
        return {
            "recovery_needed": False,
            "recovery_type": "none",
            "reason": "fallback decision"
        }