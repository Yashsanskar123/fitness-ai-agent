from app.agent.executor import Executor
from app.agent.planner import Planner
from app.memory.memory_manager import MemoryManager

from app.llm.workout_generator import WorkoutGenerator
from app.llm.diet_generator import DietGenerator

from app.agent.insight_engine import InsightEngine
from app.agent.nudge_engine import NudgeEngine
from app.agent.progress_tracker import ProgressTracker
from app.agent.recovery_advisor import RecoveryAdvisor

from app.agent.reflection_engine import ReflectionEngine
from app.agent.response_composer import ResponseComposer
from app.agent.adaptive_engine import AdaptiveEngine


def run_test():
    print("\n🚀 FULL AGENT SYSTEM TEST\n")

    # 🧠 Core Components
    planner = Planner()
    memory = MemoryManager()
    reflection = ReflectionEngine()
    composer = ResponseComposer()
    adaptive = AdaptiveEngine()

    # 🧰 Tools Registry
    tools = {
        "workout_generator": WorkoutGenerator(),
        "diet_generator": DietGenerator(),
        "progress_tracker": ProgressTracker(),
        "insight_generator": InsightEngine(),
        "nudge_generator": NudgeEngine(),
        "recovery_advisor": RecoveryAdvisor(),
    }

    executor = Executor(tools)

    # 🧪 TEST INPUTS (FULL COVERAGE)
    test_inputs = [
        "give workout",
        "give me chest workout",
        "give me a diet plan",
        "I feel sore",
        "improve my body",
        "bhai kuch bata"
    ]

    # 🔁 RUN ALL TEST CASES
    for i, user_input in enumerate(test_inputs):
        print("\n" + "="*60)
        print(f"🧪 TEST {i+1}: {user_input}")
        print("="*60)

        # 🧠 Load context
        context = memory.build_user_context(1)
        print("\n🧠 CONTEXT SNAPSHOT:")
        print({
            "recent_workouts": [w.get("workout_done") for w in context.get("recent_workouts", [])[:3]],
            "recent_diet": context.get("recent_diet", [])[:1],
            "progress": context.get("progress", [])[:1]
        })

        # 🧠 PLAN
        plan = planner.create_plan(user_input, context)
        print("\n📋 PLAN:", plan)

        # 🔥 ADAPT
        plan = adaptive.adapt_plan(plan, context, user_input)
        print("\n🧠 ADAPTED PLAN:", plan)

        # ⚙️ EXECUTE
        results = executor.execute_plan(plan, 1, user_input, context)

        # 🔄 Reload context after execution (important)
        context = memory.build_user_context(1)

        # 🧪 RAW RESULTS
        print("\n🧪 RAW RESULTS:")
        for r in results:
            print(r)

        # 🤔 REFLECTION
        results = reflection.reflect_and_fix(
            results, executor, plan, 1, user_input, context
        )

        # 🧪 AFTER REFLECTION
        print("\n🧪 AFTER REFLECTION:")
        for r in results:
            print(r)

        # 🎯 FINAL RESPONSE
        final_output = composer.compose(results)

        print("\n🔥 FINAL RESPONSE:\n")
        print(final_output)

    print("\n✅ ALL TESTS COMPLETED\n")


if __name__ == "__main__":
    run_test()