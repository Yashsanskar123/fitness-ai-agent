from app.agent.form_safety_engine import FormSafetyEngine
from app.llm.workout_generator import WorkoutGenerator

llm = WorkoutGenerator()
engine = FormSafetyEngine(llm=llm)

workout = {
    "day": "Leg Day",
    "exercises": [
        {"name": "barbell squat", "sets": 4, "reps": "8-12"},
        {"name": "leg press", "sets": 3, "reps": "10-12"}
    ]
}

injuries = ["knee pain"]
phase = "foundation"

result = engine.apply_form_safety(workout, injuries, phase)

print("\n--- FORM SAFE WORKOUT ---\n")
print(result)