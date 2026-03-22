from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()


class Planner:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # ✅ Allowed tools
        self.VALID_TOOLS = {
            "workout_generator",
            "diet_generator",
            "progress_tracker",
            "recovery_advisor",
            "insight_generator",
            "nudge_generator",
        }

    # ---------------- SAFE JSON PARSER ---------------- #

    def safe_parse(self, output):
        try:
            return json.loads(output)
        except:
            output = output.strip()
            output = re.sub(r"```json|```", "", output)

            match = re.search(r"\[.*\]", output, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return []

        return []

    # ---------------- VALIDATE PLAN ---------------- #

    def validate_plan(self, plan):
        if not isinstance(plan, list):
            return []

        valid_steps = []

        for step in plan:
            tool = step.get("tool")
            args = step.get("args", {})

            if tool in self.VALID_TOOLS:
                valid_steps.append({
                    "tool": tool,
                    "args": args if isinstance(args, dict) else {}
                })

        return valid_steps

    # ---------------- MAIN PLANNER ---------------- #

    def create_plan(self, user_input, context):

        prompt = f"""
You are an AI planner.

User Input:
{user_input}

Context:
{context}

Available Tools:
- workout_generator
- diet_generator
- progress_tracker
- recovery_advisor
- insight_generator
- nudge_generator

Task:
Break the request into steps using tools.

STRICT RULES (VERY IMPORTANT):

1. If user asks for workout:
   → ONLY use workout_generator

2. ALWAYS extract parameters from input:
   - chest, legs, back → focus
   - light, easy → intensity = low
   - heavy, intense → intensity = high

3. If workout_generator is used:
   → YOU MUST include "args"
   → NEVER leave args empty

4. If user asks for diet:
   → ONLY use diet_generator

5. If user says improve / analyze:
   → use insight + workout + diet

6. If user says sore / pain:
   → use recovery_advisor

7. DO NOT include unnecessary tools

Example:
User: "light chest workout"

Output:
[
  {{
    "tool": "workout_generator",
    "args": {{
      "focus": "chest",
      "intensity": "low"
    }}
  }}
]

Return ONLY JSON array.
"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
            )

            output = response.choices[0].message.content

            plan = self.safe_parse(output)

            # ✅ KEEP ARGS (FIXED)
            plan = self.validate_plan(plan)

            user_input_lower = user_input.lower()

            casual_keywords = ["bhai","kuch","bata","hello","hi","kya"]

            if any(word in user_input_lower for word in casual_keywords):
                return [{"tool": "nudge_generator"}]

            # 🚨 FALLBACK (never empty)
            if not plan:
                user_input_lower = user_input.lower()

                if "improve" in user_input_lower or "better" in user_input_lower:
                    return [
                        {"tool": "insight_generator"},
                        {"tool": "workout_generator"},
                        {"tool": "diet_generator"},
                    ]

                elif "diet" in user_input_lower or "eat" in user_input_lower:
                    return [{"tool": "diet_generator"}]

                elif "workout" in user_input_lower:
                    return [{
                        "tool": "workout_generator",
                        "args": {"focus": "general", "intensity": "medium"}
                    }]

                elif "progress" in user_input_lower:
                    return [{"tool": "progress_tracker"}]

                elif "sore" in user_input_lower or "pain" in user_input_lower:
                    return [{"tool": "recovery_advisor"}]

                else:
                    return [{"tool": "nudge_generator"}]

            return plan

        except Exception as e:
            print("❌ PLANNER ERROR:", str(e))

            return [{"tool": "nudge_generator"}]