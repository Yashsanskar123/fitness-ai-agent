from datetime import datetime
from app.agent.consistency_engine import ConsistencyEngine
from app.agent.insight_engine import InsightEngine
from app.agent.progression_engine import ProgressionEngine
from app.agent.self_learning_engine import SelfLearningEngine
from app.agent.goal_phase_engine import GoalPhaseEngine
from app.agent.performance_engine import PerformanceEngine
from app.agent.recovery_engine import RecoveryEngine
from app.agent.missed_workout_engine import MissedWorkoutEngine

class AdaptiveEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm
        self.insight_engine = InsightEngine(llm)

        self.progression_engine = ProgressionEngine(memory_manager) if memory_manager else None
        self.learning_engine = SelfLearningEngine(memory_manager, llm) if memory_manager else None
        self.goal_phase_engine = GoalPhaseEngine(memory_manager, llm) if memory_manager else None
        self.performance_engine = PerformanceEngine(memory_manager, llm) if memory_manager else None
        self.recovery_engine = RecoveryEngine(memory_manager, llm) if memory_manager else None
        self.missed_workout_engine = MissedWorkoutEngine(memory_manager, llm) if memory_manager else None

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

    def _llm_decide(self, consistency, progression, performance, learning, goal_phase, user_input):

        goal_phase = goal_phase or {"phase": "foundation", "reason": "no data"}
        performance = performance or {
            "performance_status": "unknown",
            "fatigue_level": "medium",
            "recommendation": "maintain"
        }

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

User performance:
- Status: {performance.get("performance_status")}
- Fatigue: {performance.get("fatigue_level")}
- Recommendation: {performance.get("recommendation")}

User training phase:
- Phase: {goal_phase.get("phase")}
- Reason: {goal_phase.get("reason")}

Past learning:
- Summary: {learning.get('summary')}
- Preferred Bias: {learning.get('bias')}

Goal:
Choose the MOST appropriate training action for TODAY.

Actions:
increase_intensity
reduce_intensity
maintain
deload

Guidelines:
- High fatigue → deload
- Low consistency → reduce_intensity
- Plateau → increase_intensity
- Good progress → maintain or increase
- If performance declining → reduce_intensity or deload
- If user feels strong but fatigue exists → prefer maintain over deload
- Respect training phase (foundation → lighter, strength → heavier)
- Learning bias should influence but NOT dominate
- Prioritize safety and sustainability over aggression

Return ONLY ONE WORD from the actions above.
Do NOT explain.
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
        performance = None
        action = "maintain"
        reasoning = ""
        goal_phase = None
        recovery = None
        missed_workout = None

        # ---------------------------
        # 🧠 Multi-signal analysis
        # ---------------------------
        if self.consistency_engine:
            try:
                consistency = self.consistency_engine.analyze(user_id=user_id)

                # ---------------------------
                # 📈 Progression
                # ---------------------------
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

                if self.missed_workout_engine:
                    missed_workout = self.missed_workout_engine.analyze(
                        user_id = user_id,
                        context = context,
                        consistency = consistency
                    )

                    print("Missed Workout Decision:", missed_workout)

                # ---------------------------
                # 📊 Performance
                # ---------------------------
                if self.performance_engine:
                    performance = self.performance_engine.analyze(user_id=user_id)
                    print("📊 Performance Data:", performance)
                else:
                    performance = {
                        "performance_status": "unknown",
                        "fatigue_level": "medium",
                        "recommendation": "maintain"
                    }

                # ---------------------------
                # 💀 Recovery Engine (NEW)
                # ---------------------------
                if self.recovery_engine:
                    recovery = self.recovery_engine.analyze(
                        user_id=user_id,
                        context=context,
                        consistency=consistency,
                        performance=performance,
                        user_input=user_input
                    )
                    print("💀 Recovery Decision:", recovery)

                # ---------------------------
                # 🎯 Goal Phase
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
                # 🧠 Learning
                # ---------------------------
                if self.learning_engine:
                    learning = self.learning_engine.analyze(user_id=user_id)
                else:
                    learning = {"summary": "none", "bias": "neutral"}

                print("🧠 Learning Data:", learning)

                # ---------------------------
                # 🤖 LLM Decision
                # ---------------------------
                if self.llm:
                    action = self._llm_decide(
                        consistency,
                        progression,
                        performance,
                        learning,
                        goal_phase,
                        user_input
                    )
                else:
                    action = consistency["recommended_action"]

                print("🧠 Initial Action:", action)

                # ---------------------------
                # 📊 Performance Override
                # ---------------------------
                if performance:
                    if performance.get("recommendation") == "deload":
                        action = "deload"
                    elif performance.get("recommendation") == "reduce_intensity":
                        action = "reduce_intensity"

                # ---------------------------
                # 💀 RECOVERY OVERRIDE (CRITICAL FIX)
                # ---------------------------
                if recovery and recovery.get("recovery_needed"):

                    rec_type = recovery.get("recovery_type", "light")

                    if rec_type == "rest":
                        action = "deload"
                        reasoning = "Your body needs full recovery. Taking rest today."

                    elif rec_type == "light":
                        action = "reduce_intensity"
                        reasoning = "You are fatigued. Let's go light today."

                    elif rec_type == "deload":
                        action = "deload"
                        reasoning = "Deload recommended to prevent burnout."

                    print("💀 Recovery Override Applied:", action)

                # ---------------------------
                # 💬 Final Reasoning
                # ---------------------------
                if not reasoning:
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

                if missed_workout and missed_workout.get("adjust_plan"):
                    strategy = missed_workout.get("strategy")
                    new_focus = missed_workout.get("new_focus")

                    if strategy == "shift" and new_focus:
                        focus = new_focus
                    elif strategy == "restart":
                        focus = "full body"
                        intensity = "low"
                    elif strategy == "skip":
                        pass

                    print("Missed Workout Applied:", strategy, focus)

                # Avoid repetition
                if "chest" in last_workout and focus == "chest":
                    focus = "back"
                elif "back" in last_workout and focus == "back":
                    focus = "legs"
                elif "legs" in last_workout and focus == "legs":
                    focus = "upper body"

                # Recovery from user input
                if "sore" in user_input or "pain" in user_input:
                    intensity = "low"
                    focus = "full body"

                # No activity
                if len(workouts) == 0:
                    intensity = "low"
                    focus = "full body"

                # AI decision override
                if action == "increase_intensity":
                    intensity = "high"
                elif action == "reduce_intensity":
                    intensity = "low"
                elif action == "deload":
                    intensity = "low"
                    focus = "full body"

                # Phase adjustment
                if goal_phase:
                    phase = goal_phase.get("phase")

                    if phase == "foundation":
                        intensity = "low"
                    elif phase == "hypertrophy" and intensity == "low":
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