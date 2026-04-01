from app.llm.diet_generator import DietGenerator


def test_diet():
    print("\n🔥 TESTING DIET GENERATOR 🔥\n")

    diet = DietGenerator()

    result = diet.generate_diet(user_id=1)

    print("📦 RAW RESULT:")
    print(result)

    print("\n📊 CHECKS:")

    # ✅ Check 1: result is dict
    print("Is dict:", isinstance(result, dict))

    # ✅ Check 2: meals exist
    meals = result.get("meals", [])
    print("Meals present:", bool(meals))

    # ✅ Check 3: number of meals
    print("Meals count:", len(meals))

    # ✅ Check 4: sample meal
    if meals:
        print("\n🍽️ Sample Meal:")
        print(meals[0])

    print("\n✅ TEST COMPLETE\n")


if __name__ == "__main__":
    test_diet()