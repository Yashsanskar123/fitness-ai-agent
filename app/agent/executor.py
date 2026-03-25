from app.agent.form_safety_engine import FormSafetyEngine


class Executor:
    def __init__(self, tools):
        self.tools = tools

        # 🔥 Tool → method mapping
        self.tool_method_map = {
            "workout_generator": "generate_workout",
            "diet_generator": "generate_meal_plan",
            "progress_tracker": "get_progress",
            "recovery_advisor": "get_recovery_advice",
            "insight_generator": "generate_insights",
            "nudge_generator": "generate_nudges",
        }

        # ---------------------------
        # 💀 Engine Initializations
        # ---------------------------

        try:
            from app.agent.substitution_engine import SubstitutionEngine
            from app.llm.workout_generator import WorkoutGenerator
            self.substitution_engine = SubstitutionEngine(llm=WorkoutGenerator())
        except Exception as e:
            print("⚠️ Substitution Engine init failed:", e)
            self.substitution_engine = None

        try:
            from app.llm.workout_generator import WorkoutGenerator
            self.form_safety_engine = FormSafetyEngine(llm=WorkoutGenerator())
        except Exception as e:
            print("⚠️ FormSafety Engine init failed:", e)
            self.form_safety_engine = None

        try:
            from app.agent.multiday_engine import MultiDayEngine
            from app.llm.workout_generator import WorkoutGenerator
            self.multiday_engine = MultiDayEngine(llm=WorkoutGenerator())
        except Exception as e:
            print("⚠️ MultiDay Engine init failed:", e)
            self.multiday_engine = None

        try:
            from app.agent.nutrition_engine import NutritionEngine
            from app.llm.workout_generator import WorkoutGenerator
            self.nutrition_engine = NutritionEngine(llm=WorkoutGenerator())
        except Exception as e:
            print("⚠️ Nutrition Engine init failed:", e)
            self.nutrition_engine = None

        try:
            from app.agent.progression_engine import ProgressionEngine
            from app.memory.memory_manager import MemoryManager
            self.progression_engine = ProgressionEngine(memory_manager=MemoryManager())
        except Exception as e:
            print("⚠️ Progression Engine init failed:", e)
            self.progression_engine = None

        try:
            from app.agent.recovery_engine import RecoveryEngine
            from app.memory.memory_manager import MemoryManager
            from app.llm.workout_generator import WorkoutGenerator

            self.recovery_engine = RecoveryEngine(
                memory_manager=MemoryManager(),
                llm=WorkoutGenerator()
            )
        except Exception as e:
            print("⚠️ Recovery Engine init failed:", e)
            self.recovery_engine = None

    # ==========================================================
    # 🚀 MAIN EXECUTION
    # ==========================================================
    def execute_plan(self, plan, user_id, user_input, context):

        # 💀 MULTI-DAY TRIGGER
        try:
            if self.multiday_engine:
                if "plan" in user_input.lower() or "week" in user_input.lower():
                    print("📅 Generating multi-day plan...")
                    multiday = self.multiday_engine.generate_plan(context, user_id)

                    return [{
                        "tool": "multiday_planner",
                        "output": multiday
                    }]
        except Exception as e:
            print("⚠️ MultiDay Trigger Error:", e)

        results = []

        # ==========================================================
        # 🔁 EXECUTION LOOP
        # ==========================================================
        for step in plan:
            tool_name = step.get("tool")
            args = step.get("args", {}) or {}

            print(f"⚙️ Executing: {tool_name}")

            tool = self.tools.get(tool_name)

            if not tool:
                results.append({"error": f"{tool_name} not found"})
                continue

            try:
                method_name = self.tool_method_map.get(tool_name)

                if not method_name or not hasattr(tool, method_name):
                    results.append({
                        "tool": tool_name,
                        "error": f"Method {method_name} not found"
                    })
                    continue

                method = getattr(tool, method_name)

                # 🧠 Inject defaults
                if tool_name == "workout_generator":
                    args.setdefault("user_id", user_id)
                    args.setdefault("user_input", user_input)

                elif tool_name == "diet_generator":
                    args.setdefault("user_id", user_id)

                elif tool_name in ["insight_generator", "nudge_generator", "progress_tracker"]:
                    args.setdefault("context", context)

                elif tool_name == "recovery_advisor":
                    args = {"user_input": user_input}

                # 🚀 Execute
                result = method(**args)
                print("RAW TOOL OUTPUT:", result)

                # ==================================================
                # 💀 WORKOUT POST PROCESSING
                # ==================================================
                if tool_name == "workout_generator":

                    injuries = context.get("injuries", [])
                    print("🩹 Injuries:", injuries)

                    # ==================================================
                    # 💀 RECOVERY ENGINE (FIRST 🔥)
                    # ==================================================
                    try:
                        if self.recovery_engine:

                            print("🧠 Applying recovery logic...")

                            recovery = self.recovery_engine.analyze(
                                user_id=user_id,
                                context=context,
                                consistency=context.get("consistency", {}),
                                performance=context.get("performance", {}),
                                user_input=user_input
                            )

                            r_type = recovery.get("recovery_type")

                            if recovery.get("recovery_needed"):

                                if r_type == "rest":
                                    result["note"] = "Rest day recommended"
                                    result["exercises"] = []

                                elif r_type == "light":
                                    for ex in result.get("exercises", []):
                                        if "sets" in ex:
                                            ex["sets"] = max(2, ex["sets"] - 1)

                                    result["note"] = "Light workout (recovery mode)"

                                elif r_type == "deload":
                                    for ex in result.get("exercises", []):
                                        if "sets" in ex:
                                            ex["sets"] = max(2, ex["sets"] - 1)
                                        ex["reps"] = "light"

                                    result["note"] = "Deload week activated"

                            print("✅ Recovery applied:", recovery)

                    except Exception as e:
                        print("⚠️ Recovery Error:", e)

                    # 🔁 Substitution
                    try:
                        if self.substitution_engine and injuries:
                            print("🩹 Applying substitution...")
                            result = self.substitution_engine.apply_substitutions(
                                workout_plan=result,
                                injuries=injuries
                            )
                    except Exception as e:
                        print("⚠️ Substitution Error:", e)

                    # 🧠 Form Safety
                    try:
                        if self.form_safety_engine:
                            phase = context.get("goal_phase", {}).get("phase", "foundation")

                            print("💀 Applying form safety...")
                            result = self.form_safety_engine.apply_form_safety(
                                workout_plan=result,
                                injuries=injuries,
                                phase=phase
                            )
                    except Exception as e:
                        print("⚠️ FormSafety Error:", e)

                    # 📈 Progression (CONDITIONAL 🔥)
                    try:
                        if self.progression_engine and result.get("exercises"):

                            if result.get("note") in ["Rest day recommended", "Deload week activated"]:
                                print("⛔ Skipping progression due to recovery")

                            else:
                                print("📈 Applying progression...")

                                progress_data = self.progression_engine.analyze(user_id)

                                result = self.progression_engine.apply_progression(
                                    workout_plan=result,
                                    progress_data=progress_data
                                )

                                print("✅ Progress:", progress_data["progress_status"])

                    except Exception as e:
                        print("⚠️ Progression Error:", e)

                    # 🥗 Nutrition
                    try:
                        if self.nutrition_engine:
                            print("💀 Generating diet...")

                            targets = self.nutrition_engine.analyze(
                                context=context,
                                user_id=user_id
                            )

                            diet = self.nutrition_engine.generate_meal_plan(
                                nutrition_targets=targets,
                                user_input=user_input
                            )

                            results.append({
                                "tool": "diet_generator",
                                "output": diet
                            })

                    except Exception as e:
                        print("⚠️ Nutrition Error:", e)

                # 💾 Save memory
                self.write_to_memory(tool_name, result, user_id)

                # ✅ Append main result
                results.append({
                    "tool": tool_name,
                    "output": result
                })

            except Exception as e:
                print("❌ EXECUTION ERROR:", e)
                results.append({
                    "tool": tool_name,
                    "error": str(e)
                })

        return results

    # ==========================================================
    # 💾 MEMORY
    # ==========================================================
    def write_to_memory(self, tool_name, output, user_id):
        try:
            from app.memory.memory_manager import MemoryManager
            memory = MemoryManager()

            if tool_name == "workout_generator":
                memory.save_workout(
                    user_id=user_id,
                    workout=output.get("day", ""),
                    duration=60,
                    notes="AI Generated workout"
                )

            elif tool_name == "diet_generator":
                memory.save_diet(
                    user_id=user_id,
                    meals=str(output.get("meals", [])),
                    protein=output.get("protein_target", 0),
                    calories=output.get("total_calories", 0)
                )

        except Exception as e:
            print("⚠️ Memory Write Error:", e)