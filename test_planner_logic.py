from app.agent.planner import Planner
from app.agent.executor import Executor
from app.agent.adaptive_engine import AdaptiveEngine
from app.memory.memory_manager import MemoryManager

from app.llm.workout_generator import WorkoutGenerator
from app.llm.diet_generator import DietGenerator
from app.agent.insight_engine import InsightEngine
from app.agent.nudge_engine import NudgeEngine


# ---------------- INIT ---------------- #

planner = Planner()

memory = MemoryManager()
llm = WorkoutGenerator()  # using your LLM

adaptive = AdaptiveEngine(memory_manager=memory, llm=llm)

tools = {
    "workout_generator": WorkoutGenerator(),
    "diet_generator": DietGenerator(),
    "insight_generator": InsightEngine(llm),
    "nudge_generator": NudgeEngine(llm),
    "progress_tracker": memory,
    "recovery_advisor": lambda user_input=None: {
        "advice": "Take rest and recover properly"
    }
}

executor = Executor(tools)


# ---------------- HELPER ---------------- #

def print_case(title):
    print("\n" + "="*70)
    print(f"🧪 TEST: {title}")
    print("="*70)


def run_test(user_input):
    print_case(user_input)

    # ---------------- PLANNER ---------------- #
    plan = planner.create_plan(user_input, {})
    print("\n🧠 PLANNER OUTPUT:")
    print(plan)

    if not plan:
        print("❌ Planner failed")
        return

    # ---------------- EXECUTOR ---------------- #
    result = executor.execute_plan(
        plan=plan,
        user_id=1,
        user_input=user_input,
        context=memory.build_user_context(1)
    )

    print("\n⚙️ EXECUTOR OUTPUT:")
    print(result)

    # ---------------- ADAPTIVE ---------------- #
    adapted = adaptive.adapt_plan(
        plan=plan,
        context=memory.build_user_context(1),
        user_input=user_input,
        user_id=1
    )

    print("\n🔄 ADAPTED PLAN:")
    print(adapted)

    # ---------------- ANALYSIS ---------------- #
    print("\n🔍 ANALYSIS:")

    tools = [step.get("tool") for step in plan]

    if "workout_generator" in tools:
        print("✔ Workout flow triggered")

    if "diet_generator" in tools:
        print("✔ Diet flow triggered")

    if "recovery_advisor" in tools:
        print("✔ Recovery detected")

    if "nudge_generator" in tools:
        print("✔ Nudge flow triggered")

    if "insight_generator" in tools:
        print("✔ Insight flow triggered")

    print("✔ System executed end-to-end\n")


# ---------------- TEST CASES ---------------- #

def run_all_tests():
    print("\n🔥 FULL AI SYSTEM LLM TEST 🔥\n")

    # 💪 Workout
    run_test("give me a chest workout")

    # 🥗 Diet
    run_test("what should I eat for muscle gain")

    # 🩹 Injury
    run_test("I have knee pain while squats")

    # 😴 Recovery
    run_test("I feel very tired and sore today")

    # 📈 Progress
    run_test("analyze my progress")

    # 💬 Casual
    run_test("what should I do today")

    # 🤯 Edge case
    run_test("asdfghjkl")

    print("\n✅ ALL TESTS DONE\n")


if __name__ == "__main__":
    run_all_tests()