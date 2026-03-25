from app.agent.recovery_engine import RecoveryEngine


# ---------------------------
# 🔥 MOCK MEMORY (SAFE)
# ---------------------------
class MockMemory:
    def get_recent_workouts(self, user_id):
        return [
            {"day": "chest", "intensity": "high"},
            {"day": "back", "intensity": "high"},
            {"day": "legs", "intensity": "high"},
            {"day": "shoulders", "intensity": "high"},
            {"day": "arms", "intensity": "high"},
        ]


# ---------------------------
# 🔥 MOCK LLM (TEMP)
# ---------------------------
from app.llm.workout_generator import WorkoutGenerator

llm = WorkoutGenerator()


# ---------------------------
# 🚀 TEST RUNNER
# ---------------------------
def run_test():

    engine = RecoveryEngine(
        memory_manager=MockMemory(),
        llm=WorkoutGenerator()
    )

    # 🧪 CASE 1: FATIGUE USER
    print("\n==============================")
    print("🧪 TEST 1: FATIGUE USER")
    print("==============================")

    result1 = engine.analyze(
        user_id=1,
        context={},
        consistency={
            "streak_days": 6,
            "fatigue_level": "high",
            "missed_recent": 0
        },
        performance={
            "performance_status": "declining",
            "fatigue_level": "high"
        },
        user_input="I feel very tired and sore"
    )

    print("\n✅ RESULT:", result1)

    # 🧪 CASE 2: GOOD USER
    print("\n==============================")
    print("🧪 TEST 2: FRESH USER")
    print("==============================")

    result2 = engine.analyze(
        user_id=1,
        context={},
        consistency={
            "streak_days": 2,
            "fatigue_level": "low",
            "missed_recent": 0
        },
        performance={
            "performance_status": "improving",
            "fatigue_level": "low"
        },
        user_input="I feel great and energetic"
    )

    print("\n✅ RESULT:", result2)


if __name__ == "__main__":
    run_test()