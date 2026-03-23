from app.agent.form_safety_engine import FormSafetyEngine


class Executor:
    def __init__(self, tools):
        self.tools = tools  # tool registry

        # 🔥 Map tool → method name
        self.tool_method_map = {
            "workout_generator": "generate_workout",
            "diet_generator": "generate_diet",
            "progress_tracker": "get_progress",
            "recovery_advisor": "get_recovery_advice",
            "insight_generator": "generate_insights",
            "nudge_generator": "generate_nudges",
        }

        # ---------------------------
        # 💀 Substitution Engine INIT
        # ---------------------------
        try:
            from app.agent.substitution_engine import SubstitutionEngine
            from app.llm.workout_generator import WorkoutGenerator

            self.substitution_engine = SubstitutionEngine(
                llm=WorkoutGenerator()
            )
        except Exception as e:
            print("⚠️ Substitution Engine init failed:", str(e))
            self.substitution_engine = None

        # ---------------------------
        # 💀 Form Safety Engine INIT
        # ---------------------------
        try:
            from app.llm.workout_generator import WorkoutGenerator

            self.form_safety_engine = FormSafetyEngine(
                llm=WorkoutGenerator()
            )
        except Exception as e:
            print("⚠️ FormSafety Engine init failed:", str(e))
            self.form_safety_engine = None

    def execute_plan(self, plan, user_id, user_input, context):
        results = []

        for step in plan:
            tool_name = step.get("tool")
            args = step.get("args", {}) or {}

            print(f"⚙️ Executing: {tool_name}")

            tool = self.tools.get(tool_name)

            if not tool:
                results.append({"error": f"{tool_name} not found"})
                continue

            try:
                # 🔥 Get method dynamically
                method_name = self.tool_method_map.get(tool_name)

                if not method_name or not hasattr(tool, method_name):
                    results.append({
                        "tool": tool_name,
                        "error": f"Method {method_name} not found in {tool_name}"
                    })
                    continue

                method = getattr(tool, method_name)

                # 🧠 Inject default args (auto-fill)
                if tool_name == "workout_generator":
                    args.setdefault("user_id", user_id)
                    args.setdefault("user_input", user_input)

                elif tool_name == "diet_generator":
                    args.setdefault("user_id", user_id)

                elif tool_name in ["insight_generator", "nudge_generator", "progress_tracker"]:
                    args.setdefault("context", context)

                elif tool_name == "recovery_advisor":
                    args = {"user_input": user_input}

                # 🚀 FINAL CALL (dynamic)
                result = method(**args)
                print("RAW TOOL OUTPUT:", result)

                # ==================================================
                # 💀 POST-PROCESSING FOR WORKOUT (IMPORTANT ORDER)
                # ==================================================
                if tool_name == "workout_generator":

                    injuries = context.get("injuries", [])
                    print("🩹 Injuries in Executor:", injuries)

                    # ---------------------------
                    # 💀 APPLY SUBSTITUTION
                    # ---------------------------
                    try:
                        if self.substitution_engine and injuries:
                            print("🩹 Applying substitution...")

                            result = self.substitution_engine.apply_substitutions(
                                workout_plan=result,
                                injuries=injuries
                            )

                            print("✅ Post-substitution workout:", result)

                    except Exception as e:
                        print("⚠️ Substitution Error:", str(e))

                    # ---------------------------
                    # 💀 APPLY FORM SAFETY
                    # ---------------------------
                    try:
                        if self.form_safety_engine:

                            # 🔥 get phase if available
                            phase = "foundation"
                            if context.get("goal_phase"):
                                phase = context["goal_phase"].get("phase", "foundation")

                            print("💀 Applying form safety...")

                            result = self.form_safety_engine.apply_form_safety(
                                workout_plan=result,
                                injuries=injuries,
                                phase=phase
                            )

                            print("✅ Form safety added")

                    except Exception as e:
                        print("⚠️ FormSafety Error:", str(e))

                # ---------------------------
                # 💾 MEMORY WRITE
                # ---------------------------
                self.write_to_memory(tool_name, result, user_id)

                results.append({
                    "tool": tool_name,
                    "output": result
                })

            except Exception as e:
                print("❌ EXECUTION ERROR:", str(e))
                results.append({
                    "tool": tool_name,
                    "error": str(e)
                })

        return results

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
            print("Memory Write Error:", str(e))