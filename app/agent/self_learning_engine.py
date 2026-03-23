class SelfLearningEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def analyze(self, user_id=1):

        if not self.memory:
            return None

        # ---------------------------
        # 📊 Get past learning
        # ---------------------------
        learning_data = self.memory.get_recent_learning(user_id)

        if not learning_data:
            return {
                "summary": "No past learning available",
                "bias": "neutral"
            }

        # ---------------------------
        # 🤖 LLM Analysis
        # ---------------------------
        if self.llm:
            return self._llm_analyze(learning_data)

        # ---------------------------
        # 🔁 Fallback
        # ---------------------------
        return self._rule_based_analysis(learning_data)

    # ---------------------------
    # 🤖 LLM LEARNING
    # ---------------------------
    def _llm_analyze(self, learning_data):

        prompt = f"""
You are an intelligent fitness coach AI.

Here are past decisions and outcomes:

{learning_data}

Analyze patterns and answer:

1. What decisions worked well?
2. What should we prefer going forward?

Return in JSON:

{{
  "summary": "...",
  "bias": "increase_intensity / reduce_intensity / maintain / deload"
}}
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            # Clean response
            response = response.strip()
            response = re.sub(r"```json|```", "", response)

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                json_str = match.group(0)
                try:
                    return json.loads(json_str)
                except:
                    print("Json parse failed", json_str)
            return self._rule_based_analysis(learning_data)

        except Exception as e:
            print("⚠️ Learning LLM error:", str(e))
            return self._rule_based_analysis(learning_data)

    # ---------------------------
    # 🔁 FALLBACK
    # ---------------------------
    def _rule_based_analysis(self, learning_data):

        success_count = 0

        for item in learning_data:
            outcome = item.get("outcome", {})
            if outcome.get("completed"):
                success_count += 1

        if success_count >= len(learning_data) / 2:
            return {
                "summary": "Most plans are working well",
                "bias": "maintain"
            }

        return {
            "summary": "Adjustments may be needed",
            "bias": "reduce_intensity"
        }