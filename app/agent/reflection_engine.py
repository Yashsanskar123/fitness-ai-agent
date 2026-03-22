class ReflectionEngine:
    def __init__(self):
        pass

    def is_bad_output(self, tool_name, output):
        if not output:
            return True

        if tool_name == "workout_generator":
            return not output.get("exercises")

        elif tool_name == "diet_generator":
            return (
                not output.get("meals")
                or output.get("total_calories", 0) == 0
            )

        elif tool_name == "insight_generator":
            return not output or len(output) == 0
        
        elif tool_name == "recovery_advisor":
            return not output or not output.get("advice")

        return False

    def reflect_and_fix(self, results, executor,plan, user_id, user_input, context):
        fixed_results = []

        for i, res in enumerate(results):
            tool_name = res.get("tool","unknown")
            output = res.get("output")

            if not tool_name or "error" in res:
                fixed_results.append(res)
                continue

            if self.is_bad_output(tool_name, output):
                print(f"🤔 Reflection: Fixing {tool_name}...")

                # 🔁 Retry ONLY this tool
                retry_plan = [plan[i]]
                retry_result = executor.execute_plan(
                    retry_plan, user_id, user_input, context
                )

                # Replace with retry result
                if retry_result and "output" in retry_result[0]:
                    fixed_results.append(retry_result[0])
                else:
                    fixed_results.append(res)

            else:
                fixed_results.append(res)

        return fixed_results