# test_progression_feature.py

from app.agent.progression_engine import ProgressionEngine
from app.memory.memory_manager import MemoryManager


def run_progression_test():

    print("\n" + "="*60)
    print("🧪 TEST: Progression Engine (Feature Test)")
    print("="*60)

    memory = MemoryManager()
    engine = ProgressionEngine(memory_manager=memory)

    # 🔥 Step 1: Analyze
    progress_data = engine.analyze(user_id=1)

    print("\n📊 Progress Analysis:")
    print(progress_data)

    # 🔥 Step 2: Dummy Workout
    workout = {
        "day": "Test Day",
        "exercises": [
            {"name": "Bench Press", "sets": 3, "reps": "8-12"},
            {"name": "Squats", "sets": 3, "reps": "8-12"},
        ]
    }

    # 🔥 Step 3: Apply Progression
    updated_workout = engine.apply_progression(
        workout_plan=workout,
        progress_data=progress_data
    )

    # 🔥 Step 4: Check Deload
    if engine.check_deload(progress_data):
        print("\n⚠️ Deload Triggered")
        for ex in updated_workout["exercises"]:
            ex["sets"] = max(2, ex["sets"] - 1)

    print("\n🏋️ Updated Workout:")
    for ex in updated_workout["exercises"]:
        print(ex)


if __name__ == "__main__":
    run_progression_test()