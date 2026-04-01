from app.agent.performance_engine import PerformanceEngine
from app.memory.memory_manager import MemoryManager
from app.llm.workout_generator import WorkoutGenerator

engine = PerformanceEngine(
    memory_manager=MemoryManager(),
    llm=WorkoutGenerator()
)

result = engine.analyze(user_id=1)
print(result)