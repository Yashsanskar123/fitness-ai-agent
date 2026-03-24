class MissedWorkoutEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def analyze(self, user_id=1, context=None, consistency=None):
        """
        Detect missed workouts and suggest plan adjustment
        """

        context = context or {}
        consistency = consistency or {}

        workouts = context.get("recent_workouts", []) or []

        # ---------------------------
        # 🧠 BASIC SIGNALS
        # ---------------------------
        missed_recent = consistency.get("missed_recent", 0)
        streak = consistency.get("streak_days", 0)

        # ---------------------------
        # 🤖 LLM DECISION
        # ---------------------------
        if self.llm:
            return self._llm_decide(workouts, consistency)

        # ---------------------------
        # 🔁 FALLBACK LOGIC
        # ---------------------------
        if missed_recent >= 3:
            return {
                "adjust_plan": True,
                "strategy": "restart",
                "new_focus": "full body",
                "reason": "Multiple missed workouts, restarting plan"
            }

        elif missed_recent == 1:
            last = workouts[0]["workout_done"].lower() if workouts else "full body"

            return {
                "adjust_plan": True,
                "strategy": "shift",
                "new_focus": last,
                "reason": "Missed one workout, shifting focus"
            }

        return {
            "adjust_plan": False,
            "strategy": "none",
            "new_focus": None,
            "reason": "No major disruption"
        }

    # ---------------------------
    # 🤖 LLM DECISION
    # ---------------------------
    def _llm_decide(self, workouts, consistency):

        prompt = f"""
You are a fitness planning assistant.

Recent workouts:
{workouts}

Consistency:
- Streak: {consistency.get("streak_days")}
- Missed Days: {consistency.get("missed_recent")}

Decide:
- Should we adjust the workout plan?
- If yes, how?

Strategies:
shift → move missed workout to today
skip → continue current plan
restart → start fresh (light training)

Return ONLY JSON:

{{
  "adjust_plan": true/false,
  "strategy": "shift/skip/restart",
  "new_focus": "...",
  "reason": "..."
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
                print("💀 Missed Workout Decision:", data)
                return data

        except Exception as e:
            print("⚠️ MissedWorkout LLM error:", str(e))

        return {
            "adjust_plan": False,
            "strategy": "none",
            "new_focus": None,
            "reason": "fallback"
        }