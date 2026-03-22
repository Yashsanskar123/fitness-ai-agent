from app.llm.workout_generator import WorkoutGenerator
from app.llm.diet_generator import DietGenerator
from app.memory.memory_manager import MemoryManager


class FitnessAgent:
    def __init__(self):
        self.workout_gen = WorkoutGenerator()
        self.diet_gen = DietGenerator()
        self.memory = MemoryManager()

    def detect_intent(self, user_input: str):
        user_input = user_input.lower()

        if "workout" in user_input:
            return "workout"
        elif "diet" in user_input or "meal" in user_input:
            return "diet"
        elif "progress" in user_input or "weight" in user_input:
            return "progress"
        elif "tired" in user_input or "sore" in user_input:
            return "recovery"
        else:
            return "general"

    def run(self, user_input: str, user_id=1):

        intent = self.detect_intent(user_input)

        # 🔥 Decision Layer
        if intent == "workout":
            return self.workout_gen.generate_workout(user_id, user_input)

        elif intent == "diet":
            return self.diet_gen.generate_diet(user_id)

        elif intent == "progress":
            return self.memory.get_progress_history(user_id)

        elif intent == "recovery":
            return {
                "advice": "Take a rest day, hydrate well, and focus on light stretching."
            }

        else:
            return {
                "message": "I can help with workouts, diet, and progress tracking."
            }