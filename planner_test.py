from app.agent.planner import Planner

planner = Planner()

tests = [
    "light chest workout",
    "give me diet plan",
    "i have knee pain",
    "track my progress",
    "hi bhai",
    "asdfghjkl"
]

for t in tests:
    print("\nINPUT:", t)
    print("OUTPUT:", planner.create_plan(t, {}))