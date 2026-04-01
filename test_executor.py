from app.agent.planner import Planner
from app.agent.executor import Executor
from app.memory.memory_manager import MemoryManager
from app.agent.progress_tracker import ProgressTracker
from app.llm.workout_generator import WorkoutGenerator
from app.llm.diet_generator import DietGenerator
from app.agent.insight_engine import InsightEngine
from app.agent.nudge_engine import NudgeEngine

# ---------------- INIT ---------------- #
planner = Planner()
memory_manager = MemoryManager()
llm = WorkoutGenerator()
progress_tracker = ProgressTracker()

tools = {
    "workout_generator": WorkoutGenerator(),
    "diet_generator": DietGenerator(),
    "insight_generator": InsightEngine(llm),
    "nudge_generator": NudgeEngine(llm),
    "progress_tracker": lambda user_id = 1, **kwargs: progress_tracker.get_progress(memory_manager.build_user_context(user_id)),
    "recovery_advisor": lambda user_input=None: {
        "advice": "Take rest and recover"
    }
}

executor = Executor(tools)


# ---------------- SAFE PRINT ---------------- #
def compact_output(result):
    compact = []

    for r in result:
        tool = r.get("tool")
        output = r.get("output", {})
        error = r.get("error")

        if error:
            compact.append({"tool": tool, "error": error})
            continue

        # 🔥 reduce heavy output
        if tool == "workout_generator":
            compact.append({
                "tool": tool,
                "day": output.get("day"),
                "exercises_count": len(output.get("exercises", [])),
                "note": output.get("note")
            })

        elif tool == "diet_generator":
            compact.append({
                "tool": tool,
                "meals_count": len(output.get("meals", []))
            })

        else:
            compact.append({
                "tool": tool,
                "output_keys": list(output.keys()) if isinstance(output, dict) else output
            })

    return compact


# ---------------- RUN TEST ---------------- #
def run_test(query):
    print("\n" + "="*60)
    print(f"🧠 INPUT: {query}")

    # Planner
    plan = planner.create_plan(query, {})
    print("📌 PLAN:", plan)

    # Executor
    result = executor.execute_plan(
        plan=plan,
        user_id=1,
        user_input=query,
        context=memory_manager.build_user_context(1)
    )

    # Compact Output
    compact = compact_output(result)

    print("⚙️ RESULT:", compact)


# ---------------- TEST CASES ---------------- #
def run_all():
    print("\n🔥 COMPACT EXECUTOR TEST 🔥")

    run_test("give me chest workout")
    run_test("give me diet plan for muscle gain")
    run_test("i have knee pain")
    run_test("track my progress")
    run_test("hi bhai")
    run_test("asdfghjkl")

    print("\n✅ DONE\n")


if __name__ == "__main__":
    run_all()