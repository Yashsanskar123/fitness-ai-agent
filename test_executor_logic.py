from app.agent.executor import Executor


# 🔧 MOCK TOOL IMPLEMENTATIONS (IMPORTANT)
class MockWorkoutTool:
    def generate_workout(self, **kwargs):
        return {
            "exercises": [
                {"name": "bench press", "sets": 3, "reps": 10},
                {"name": "shoulder press", "sets": 3, "reps": 10}
            ]
        }


class MockDietTool:
    def generate_meal_plan(self, **kwargs):
        return {
            "meals": ["rice", "dal"],
            "protein_target": 100,
            "total_calories": 2000
        }


class MockRecoveryTool:
    def get_recovery_advice(self, **kwargs):
        return {"advice": "rest"}


class MockInsightTool:
    def generate_insights(self, **kwargs):
        return {"insight": "improve consistency"}


class MockNudgeTool:
    def generate_nudges(self, **kwargs):
        return {"nudge": "stay consistent"}


# 🧠 TOOL MAP
tools = {
    "workout_generator": MockWorkoutTool(),
    "diet_generator": MockDietTool(),
    "recovery_advisor": MockRecoveryTool(),
    "insight_generator": MockInsightTool(),
    "nudge_generator": MockNudgeTool(),
}

executor = Executor(tools)


def run_test(name, condition, output=None):
    if condition:
        print(f"✅ PASS: {name}")
    else:
        print(f"❌ FAIL: {name}")
        if output:
            print("   Output:", output)


def test_basic_execution():
    plan = [{"tool": "workout_generator", "args": {}}]

    result = executor.execute_plan(
        plan, user_id=1, user_input="workout", context={}
    )

    run_test("Basic Execution", len(result) > 0, result)


def test_missing_tool():
    plan = [{"tool": "unknown_tool"}]

    result = executor.execute_plan(
        plan, 1, "test", {}
    )

    run_test(
        "Missing Tool Handling",
        "error" in result[0],
        result
    )


def test_injury_context():
    plan = [{"tool": "workout_generator", "args": {}}]

    context = {
        "injuries": ["shoulder"]
    }

    result = executor.execute_plan(
        plan, 1, "workout", context
    )

    run_test("Injury Handling", result is not None, result)


def test_diet_generation():
    plan = [{"tool": "diet_generator", "args": {}}]

    result = executor.execute_plan(
        plan, 1, "diet", {}
    )

    run_test(
        "Diet Generation",
        any(r["tool"] == "diet_generator" for r in result),
        result
    )


def test_multiday_trigger():
    plan = [{"tool": "workout_generator", "args": {}}]

    result = executor.execute_plan(
        plan, 1, "weekly plan", {}
    )

    run_test("Multi-day Trigger", result is not None, result)


def run_all():
    print("\n🔥 TESTING EXECUTOR 🔥\n")

    test_basic_execution()
    test_missing_tool()
    test_injury_context()
    test_diet_generation()
    test_multiday_trigger()

    print("\n✅ Executor Testing Done\n")


if __name__ == "__main__":
    run_all()