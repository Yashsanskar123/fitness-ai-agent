from datetime import datetime
from app.agent.consistency_engine import ConsistencyEngine
from app.agent.insight_engine import InsightEngine
from app.agent.progression_engine import ProgressionEngine
from app.agent.self_learning_engine import SelfLearningEngine
from app.agent.goal_phase_engine import GoalPhaseEngine


class AdaptiveEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm
        self.insight_engine = InsightEngine(llm)

        self.progression_engine = ProgressionEngine(memory_manager) if memory_manager else None
        self.learning_engine = SelfLearningEngine(memory_manager, llm) if memory_manager else None
        self.goal_phase_engine = GoalPhaseEngine(memory_manager, llm) if memory_manager else None

        if memory_manager:
            self.consistency_engine = ConsistencyEngine(memory_manager)
        else:
            self.consistency_engine = None

    # ---------------- EXISTING LOGIC (UNCHANGED) ---------------- #

    def analyze(self, context):
        insights = []

        workouts = context.get("recent_workouts", [])
        progress = context.get("progress", [])

        if len(workouts) < 2:
            insights.append("low_activity")

        if len(progress) >= 2:
            latest = progress[0]["weight"]
            prev = progress[1]["weight"]

            if latest > prev:
                insights.append("weight_gain")
            elif latest < prev:
                insights.append("weight_loss")
            else:
                insights.append("no_change")

        return insights

    def modify_workout(self, workout_plan, insights):

        if "low_activity" in insights:
            workout_plan["note"] = "You’ve been less active. Starting light today."

            for ex in workout_plan.get("exercises", []):
                ex["sets"] = max(2, ex["sets"] - 1)

        if "weight_gain" in insights:
            workout_plan["note"] = "Progressing well. Increasing intensity."

            for ex in workout_plan.get("exercises", []):
                ex["sets"] += 1

        return workout_plan

    def generate_coaching_tip(self, insights):

        if "low_activity" in insights:
            return "Try to stay consistent. Even 30 mins daily helps."

        if "weight_gain" in insights:
            return "Great progress! Keep pushing."

        if "no_change" in insights:
            return "We need to tweak your routine for better results."

        return "Stay consistent and focused"

    # ---------------- LLM DECISION ENGINE ---------------- #

    def _llm_decide(self, consistency, progression, learning, goal_phase, user_input):

        goal_phase = goal_phase or {"phase": "foundation", "reason": "no data"}

        prompt = f"""
You are an intelligent fitness coach AI.

User input:
"{user_input}"

User behavior:
- Consistency Score: {consistency['consistency_score']}
- Streak: {consistency['streak_days']}
- Missed Days: {consistency['missed_recent']}
- Fatigue: {consistency['fatigue_level']}

User progress:
- Weight Trend: {progression['weight_trend']}
- Workout Frequency: {progression['workout_trend']}
- Intensity Trend: {progression['intensity_trend']}
- Progress Status: {progression['progress_status']}

User training phase:
- Phase: {goal_phase.get("phase")}
- Reason: {goal_phase.get("reason")}

Past learning:
- Summary: {learning.get('summary')}
- Preferred Bias: {learning.get('bias')}

Decide the best training action:

increase_intensity
reduce_intensity
maintain
deload

Rules:
- High fatigue → deload
- Low consistency → reduce_intensity
- Plateau → increase_intensity
- Good progress → maintain or increase
- If user feels strong but fatigue exists → prefer maintain over deload
- Learning bias should influence but NOT dominate

Return ONLY ONE WORD.
"""

        try:
            response = self.llm.generate(prompt)

            response = response.strip().lower()
            response = response.replace(" ", "").replace("-", "_")

            for action in ["increase_intensity", "reduce_intensity", "maintain", "deload"]:
                if action in response:
                    return action

        except Exception as e:
            print("⚠️ LLM error:", str(e))

        return consistency["recommended_action"]

    # ---------------- MAIN ADAPTATION ENGINE ---------------- #

    def adapt_plan(self, plan, context, user_input, user_id=1):
        if not plan:
            return plan

        user_input = user_input.lower()
        workouts = context.get("recent_workouts", [])

        last_workout = ""
        if workouts:
            last_workout = workouts[0].get("workout_done", "").lower()

        adapted_plan = []

        consistency = None
        progression = None
        learning = None
        action = "maintain"
        reasoning = ""
        goal_phase = None

        # ---------------------------
        # 🧠 Multi-signal analysis
        # ---------------------------
        if self.consistency_engine:
            try:
                consistency = self.consistency_engine.analyze(user_id=user_id)

                if self.progression_engine:
                    progression = self.progression_engine.analyze(user_id=user_id)
                else:
                    progression = {
                        "weight_trend": "unknown",
                        "workout_trend": "unknown",
                        "intensity_trend": "unknown",
                        "progress_status": "unknown"
                    }

                print("📈 Progression Data:", progression)

                # ---------------------------
                # 🎯 Goal Phase (FIXED)
                # ---------------------------
                if self.goal_phase_engine:
                    goal_phase = self.goal_phase_engine.analyze(
                        user_id=user_id,
                        context=context,
                        consistency=consistency,
                        progression=progression
                    )
                    print("🎯 Goal Phase:", goal_phase)

                # ---------------------------
                # 🧠 Learning layer
                # ---------------------------
                if self.learning_engine:
                    learning = self.learning_engine.analyze(user_id=user_id)
                else:
                    learning = {"summary": "none", "bias": "neutral"}

                print("🧠 Learning Data:", learning)

                # ---------------------------
                # 🤖 Final decision
                # ---------------------------
                if self.llm:
                    action = self._llm_decide(consistency, progression, learning, goal_phase, user_input)
                else:
                    action = consistency["recommended_action"]

                print("🧠 Final Action:", action)

                reasoning = self.insight_engine.generate_reasoning(consistency, action)
                print("💬 AI Reasoning:", reasoning)

            except Exception as e:
                print("⚠️ Engine Error:", str(e))
                action = "maintain"
                reasoning = "Let's continue with a balanced workout today."

        # ---------------------------
        # 🔁 Plan modification
        # ---------------------------
        for step in plan:
            tool = step.get("tool")
            args = step.get("args", {})

            if tool == "workout_generator":

                focus = args.get("focus", "full body")
                intensity = args.get("intensity", "medium")

                # Avoid repetition
                if "chest" in last_workout and focus == "chest":
                    focus = "back"
                elif "back" in last_workout and focus == "back":
                    focus = "legs"
                elif "legs" in last_workout and focus == "legs":
                    focus = "upper body"

                # Recovery override
                if "sore" in user_input or "pain" in user_input:
                    intensity = "low"
                    focus = "full body"

                # No activity
                if len(workouts) == 0:
                    intensity = "low"
                    focus = "full body"

                # ---------------------------
                # 🧠 AI decision override
                # ---------------------------
                if action == "increase_intensity":
                    intensity = "high"
                elif action == "reduce_intensity":
                    intensity = "low"
                elif action == "deload":
                    intensity = "low"
                    focus = "full body"

                # ---------------------------
                # 🎯 PHASE-BASED ADJUSTMENT (NEW)
                # ---------------------------
                if goal_phase:
                    phase = goal_phase.get("phase")

                    if phase == "foundation":
                        intensity = "low"

                    elif phase == "hypertrophy":
                        if intensity == "low":
                            intensity = "medium"

                    elif phase == "strength":
                        intensity = "high"

                    elif phase == "cut":
                        intensity = "medium"

                step["args"] = {
                    "focus": focus,
                    "intensity": intensity,
                    "reason": reasoning
                }

            adapted_plan.append(step)

        return adapted_plan