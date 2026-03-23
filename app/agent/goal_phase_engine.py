class GoalPhaseEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def analyze(self, user_id=1, context=None, consistency=None, progression=None):
        """
        Determine user's current training phase using LLM
        """

        # ---------------------------
        # 🧠 Get user context
        # ---------------------------
        if not context and self.memory:
            context = self.memory.build_user_context(user_id)

        context = context or {}

        user_profile = context.get("user_profile") or {}

        goal = user_profile.get("goal") or "general fitness"

        # fallback safety
        consistency = consistency or {}
        progression = progression or {}

        # ---------------------------
        # 🤖 LLM DECISION
        # ---------------------------
        if self.llm:
            return self._llm_decide(goal, consistency, progression)

        # ---------------------------
        # 🔁 fallback (never break system)
        # ---------------------------
        return {
            "phase": "foundation",
            "reason": "default fallback phase"
        }

    # ---------------------------
    # 🤖 LLM LOGIC
    # ---------------------------
    def _llm_decide(self, goal, consistency, progression):

        prompt = f"""
You are an expert fitness coach.

Analyze the user and determine their CURRENT training phase.

User Goal:
{goal}

Consistency:
{consistency}

Progression:
{progression}

Choose ONE phase:

- foundation (beginner / inconsistent)
- hypertrophy (muscle building phase)
- strength (advanced lifting phase)
- cut (fat loss phase)

Rules:
- Low consistency → foundation
- No progress → foundation
- Improving → hypertrophy
- High intensity focus → strength
- Fat loss goal → cut

Return ONLY JSON:

{{
  "phase": "...",
  "reason": "..."
}}
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            response = response.strip()
            response = re.sub(r"```json|```", "", response)

            # remove comments
            response = re.sub(r"//.*", "", response)

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                json_str = match.group(0)

                try:
                    data = json.loads(json_str)

                    phase = data.get("phase", "foundation").lower()

                    # 🔥 normalize phase
                    if phase not in ["foundation", "hypertrophy", "strength", "cut"]:
                        phase = "foundation"

                    data["phase"] = phase

                    print("🎯 Goal Phase:", data)

                    return data

                except:
                    print("⚠️ GoalPhase JSON parse failed:", json_str)

        except Exception as e:
            print("⚠️ GoalPhase LLM error:", str(e))

        # 🔁 fallback
        return {
            "phase": "foundation",
            "reason": "fallback due to error"
        }