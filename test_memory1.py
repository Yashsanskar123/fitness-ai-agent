# test_full_pipeline.py

from app.agent.executor import Executor
from app.llm.workout_generator import WorkoutGenerator
from app.llm.diet_generator import DietGenerator


def build_tools():
    return {
        "workout_generator": WorkoutGenerator(),
        "diet_generator": DietGenerator(),
    }


def run_test(name, user_input, context):

    print("\n" + "="*60)
    print(f"🧪 TEST: {name}")
    print("="*60)

    executor = Executor(build_tools())

    plan = [
        {
            "tool": "workout_generator",
            "args": {}
        }
    ]

    results = executor.execute_plan(
        plan=plan,
        user_id=1,
        user_input=user_input,
        context=context
    )

    print("\n🔚 FINAL OUTPUT:\n")

    for r in results:
        print(f"\n🔧 TOOL: {r.get('tool')}")
        print("OUTPUT:\n", r.get("output"))


if __name__ == "__main__":

    # 🔥 TEST 1: Normal Case
    run_test(
        name="Normal Workout",
        user_input="give me a workout plan for muscle gain",
        context={
            "user_profile": {
                "weight": 65,
                "goal": "muscle_gain",
                "activity_level": "moderate"
            },
            "injuries": []
        }
    )

    # 🔥 TEST 2: With Injury
    run_test(
        name="Workout with Knee Pain",
        user_input="leg workout",
        context={
            "user_profile": {
                "weight": 65,
                "goal": "muscle_gain",
                "activity_level": "moderate"
            },
            "injuries": [
                {
                    "injury_type": "knee pain",
                    "severity": "mild"
                }
            ]
        }
    )

    # 🔥 TEST 3: Multi-day trigger
    run_test(
        name="Weekly Plan",
        user_input="give me a weekly workout plan",
        context={
            "user_profile": {
                "weight": 65,
                "goal": "muscle_gain"
            },
            "injuries": []
        }
    )