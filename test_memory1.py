from app.agent.executor import Executor
from app.llm.workout_generator import WorkoutGenerator

# ---------------------------
# 🔧 TOOL SETUP
# ---------------------------
tools = {
    "workout_generator": WorkoutGenerator(),
}

executor = Executor(tools=tools)

# ---------------------------
# 🧠 CONTEXT (SIMULATED USER)
# ---------------------------
context = {
    "user_profile": {
        "weight": 65,
        "goal": "muscle_gain",
        "activity_level": "moderate"
    },
    "injuries": [
        {
            "injury_type": "knee pain",
            "severity": "mild",
            "notes": "pain while doing squats"
        }
    ],
    "recent_workouts": [
        {"workout_done": "chest"},
        {"workout_done": "back"}
    ],
    "goal_phase": {
        "phase": "foundation"
    }
}

# ---------------------------
# 📋 PLAN (AGENT OUTPUT SIMULATION)
# ---------------------------
plan = [
    {
        "tool": "workout_generator",
        "args": {
            "focus": "legs",
            "intensity": "medium"
        }
    }
]

# ---------------------------
# 🧑 USER INPUT
# ---------------------------
user_input = "I missed my last workout and have knee pain"

# ---------------------------
# 🚀 EXECUTE
# ---------------------------
result = executor.execute_plan(
    plan=plan,
    user_id=1,
    user_input=user_input,
    context=context
)

# ---------------------------
# 📊 OUTPUT
# ---------------------------
print("\n==============================")
print("💀 FINAL SYSTEM OUTPUT")
print("==============================\n")

for r in result:
    print(f"🔧 TOOL: {r['tool']}")
    print("OUTPUT:")
    print(r["output"])
    print("\n--------------------------\n")