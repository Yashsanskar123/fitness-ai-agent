class RecoveryEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def analyze(self, user_id=1, context=None, consistency=None, performance=None, user_input=""):
        """
        Decide whether recovery is needed (LLM-first, rule fallback)
        """

        context = context or {}
        consistency = consistency or {}
        performance = performance or {}
        user_input = (user_input or "").lower()

        # ---------------------------
        # 📊 Memory signals (SAFE)
        # ---------------------------
        recent_workouts = []
        if self.memory:
            try:
                recent_workouts = self.memory.get_recent_workouts(user_id)
            except Exception as e:
                print("⚠️ Recovery memory error:", str(e))

        # ---------------------------
        # 🤖 LLM decision (PRIMARY)
        # ---------------------------
        if self.llm:
            try:
                return self._llm_decide(
                    consistency=consistency,
                    performance=performance,
                    context=context,
                    user_input=user_input,
                    recent_workouts=recent_workouts
                )
            except Exception as e:
                print("⚠️ LLM failed, fallback to rules:", str(e))

        # ---------------------------
        # 🔁 RULE-BASED FALLBACK
        # ---------------------------
        fatigue_flag = False

        streak = consistency.get("streak_days", 0)
        fatigue_level = consistency.get("fatigue_level", "low")
        perf_fatigue = performance.get("fatigue_level", "low")

        if streak >= 5:
            fatigue_flag = True

        if fatigue_level == "high" or perf_fatigue == "high":
            fatigue_flag = True

        if any(word in user_input for word in ["tired", "sore", "low energy", "exhausted"]):
            fatigue_flag = True

        if fatigue_flag:
            return {
                "recovery_needed": True,
                "recovery_type": "light",
                "reason": "Detected fatigue via fallback logic"
            }

        return {
            "recovery_needed": False,
            "recovery_type": "none",
            "reason": "User in good condition (fallback)"
        }

    # ---------------------------
    # 🤖 LLM DECISION CORE
    # ---------------------------
    def _llm_decide(self, consistency, performance, context, user_input, recent_workouts):

        prompt = f"""
You are an elite fitness recovery coach.

Analyze whether the user needs recovery.

User Data:

Consistency:
- Streak: {consistency.get("streak_days", 0)}
- Missed Days: {consistency.get("missed_recent", 0)}
- Fatigue: {consistency.get("fatigue_level", "low")}

Performance:
- Status: {performance.get("performance_status", "unknown")}
- Fatigue: {performance.get("fatigue_level", "low")}

Recent Workouts:
{recent_workouts}

User Input:
"{user_input}"

Think carefully:
- Look for overtraining
- Fatigue accumulation
- Recovery need

Recovery types:
- rest (full rest)
- light (reduced intensity)
- deload (systematic reduction)

Return ONLY JSON:

{{
  "recovery_needed": true/false,
  "recovery_type": "rest/light/deload/none",
  "reason": "short explanation"
}}
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            # ---------------------------
            # 🧼 Clean response
            # ---------------------------
            response = response.strip()
            response = re.sub(r"```json|```", "", response)
            response = re.sub(r"//.*", "", response)

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                data = json.loads(match.group(0))

                # ---------------------------
                # 🛡️ Safety defaults
                # ---------------------------
                return {
                    "recovery_needed": bool(data.get("recovery_needed", False)),
                    "recovery_type": data.get("recovery_type", "none"),
                    "reason": data.get("reason", "LLM decision")
                }

        except Exception as e:
            print("⚠️ Recovery LLM error:", str(e))

        # ---------------------------
        # 🔁 FINAL FALLBACK
        # ---------------------------
        return {
            "recovery_needed": False,
            "recovery_type": "none",
            "reason": "LLM fallback triggered"
        }