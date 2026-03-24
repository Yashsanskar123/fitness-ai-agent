class PerformanceEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def analyze(self, user_id=1):
        """
        Analyze user performance using past workouts, progress and learning
        """

        if not self.memory:
            return self._fallback()

        # ---------------------------
        # 📊 Fetch data
        # ---------------------------
        try:
            context = self.memory.build_user_context(user_id)

            workouts = context.get("recent_workouts", []) or []
            progress = context.get("progress", []) or []
            learning = self.memory.get_recent_learning(user_id) or []

        except Exception as e:
            print("⚠️ Performance fetch error:", str(e))
            return self._fallback()

        # ---------------------------
        # 🤖 LLM ANALYSIS
        # ---------------------------
        if self.llm:
            return self._llm_analyze(workouts, progress, learning)

        # ---------------------------
        # 🔁 fallback
        # ---------------------------
        return self._rule_based(workouts, progress)

    # ---------------------------
    # 🤖 LLM ANALYSIS
    # ---------------------------
    def _llm_analyze(self, workouts, progress, learning):

        prompt = f"""
You are an expert fitness performance analyst.

User data:

Workouts:
{workouts}

Progress:
{progress}

Past Decisions & Outcomes:
{learning}

Analyze performance and return JSON:

{{
  "completion_rate": "...",
  "performance_status": "improving / stable / declining / inconsistent",
  "fatigue_level": "low / medium / high",
  "recommendation": "increase_intensity / reduce_intensity / maintain / deload"
}}

Rules:
- If workouts are frequent → good completion
- If skipped often → low completion
- If progress improving → improving
- If fatigue high → deload
- If inconsistent → reduce_intensity
- Keep values simple and realistic
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
                json_str = match.group(0)

                try:
                    data = json.loads(json_str)

                    # 🔥 SAFE NORMALIZATION
                    data["performance_status"] = data.get("performance_status", "unknown").lower()
                    data["fatigue_level"] = data.get("fatigue_level", "medium").lower()
                    data["recommendation"] = data.get("recommendation", "maintain").lower()

                    print("📊 Performance Data:", data)

                    return data

                except:
                    print("⚠️ Performance JSON parse failed:", json_str)

        except Exception as e:
            print("⚠️ Performance LLM error:", str(e))

        return self._rule_based(workouts, progress)

    # ---------------------------
    # 🔁 FALLBACK
    # ---------------------------
    def _rule_based(self, workouts, progress):

        if len(workouts) >= 3:
            status = "improving"
        elif len(workouts) == 0:
            status = "declining"
        else:
            status = "inconsistent"

        return {
            "completion_rate": "unknown",
            "performance_status": status,
            "fatigue_level": "medium",
            "recommendation": "maintain"
        }

    def _fallback(self):
        return {
            "completion_rate": "unknown",
            "performance_status": "unknown",
            "fatigue_level": "medium",
            "recommendation": "maintain"
        }