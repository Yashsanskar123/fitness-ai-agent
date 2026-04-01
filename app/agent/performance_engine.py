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
    # 🤖 LLM ANALYSIS (FIXED)
    # ---------------------------
    def _llm_analyze(self, workouts, progress, learning):

        prompt = f"""
You are a strict JSON-only fitness performance analyzer.

Analyze the data and return ONLY a JSON object.

User Data:

Workouts:
{workouts}

Progress:
{progress}

Past Decisions:
{learning}

Output format (STRICT):

{{
  "completion_rate": 0.5,
  "performance_status": "stable",
  "fatigue_level": "medium",
  "recommendation": "maintain"
}}

STRICT RULES:
- Return ONLY JSON (no explanation, no text)
- NO markdown (no ```json)
- NO code
- NO comments
- completion_rate MUST be a number (0–1)
- performance_status MUST be one of:
  improving, stable, declining, inconsistent
- fatigue_level MUST be one of:
  low, medium, high
- recommendation MUST be one of:
  increase_intensity, reduce_intensity, maintain, deload

If unsure → return reasonable defaults.

DO NOT EXPLAIN.
ONLY RETURN JSON.
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            # ---------------------------
            # 🧹 CLEAN RESPONSE
            # ---------------------------
            response = response.strip()

            # remove markdown
            response = re.sub(r"```json|```", "", response)

            # remove comments
            response = re.sub(r"//.*", "", response)

            # ---------------------------
            # 🔍 EXTRACT JSON (FIRST MATCH ONLY)
            # ---------------------------
            match = re.search(r"\{.*?\}", response, re.DOTALL)

            if match:
                json_str = match.group(0)

                try:
                    data = json.loads(json_str)

                    # ---------------------------
                    # 🔥 STRICT NORMALIZATION
                    # ---------------------------
                    normalized = {
                        "completion_rate": float(data.get("completion_rate", 0.5)),
                        "performance_status": str(data.get("performance_status", "stable")).lower(),
                        "fatigue_level": str(data.get("fatigue_level", "medium")).lower(),
                        "recommendation": str(data.get("recommendation", "maintain")).lower()
                    }

                    print("📊 Performance Data:", normalized)

                    return normalized

                except Exception as e:
                    print("⚠️ JSON parse failed:", json_str)

        except Exception as e:
            print("⚠️ Performance LLM error:", str(e))

        print("⚠️ Falling back to rule-based performance")
        return self._rule_based(workouts, progress)

    # ---------------------------
    # 🔁 RULE-BASED FALLBACK
    # ---------------------------
    def _rule_based(self, workouts, progress):

        if len(workouts) >= 3:
            status = "improving"
        elif len(workouts) == 0:
            status = "declining"
        else:
            status = "inconsistent"

        return {
            "completion_rate": 0.5,
            "performance_status": status,
            "fatigue_level": "medium",
            "recommendation": "maintain"
        }

    # ---------------------------
    # 🚨 HARD FALLBACK
    # ---------------------------
    def _fallback(self):
        return {
            "completion_rate": 0.5,
            "performance_status": "unknown",
            "fatigue_level": "medium",
            "recommendation": "maintain"
        }