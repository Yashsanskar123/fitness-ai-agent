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

        seen_tools = set()
        valid_steps = []

        for step in plan:
            tool = step.get("tool")
            args = step.get("args", {}) or {}

            # ❌ skip invalid tools
            if tool not in self.VALID_TOOLS:
                continue

            # ❌ remove duplicates
            if tool in seen_tools:
                continue

            # 🔧 ensure args always dict
            if not isinstance(args, dict):
                args = {}

            # 🔧 FIX workout args
            if tool == "workout_generator":
                args.setdefault("focus", "general")
                args.setdefault("intensity", "medium")

            valid_steps.append({
                "tool": tool,
                "args": args
            })

            seen_tools.add(tool)

        return valid_steps

    # ---------------- MAIN PLANNER ---------------- #

    def create_plan(self, user_input, context):

        user_input_lower = user_input.lower().strip()

        # ==============================
        # 🚨 HARDCODED SAFETY RULES FIRST
        # ==============================

        # 🩹 Injury / Pain → recovery (TOP PRIORITY)
        if any(word in user_input_lower for word in ["pain", "injury", "hurt", "sore"]):
            return [{"tool": "recovery_advisor"}]

        # 💬 Casual → nudge
        if any(word in user_input_lower for word in ["bhai", "hello", "hi", "kya", "hey"]):
            return [{"tool": "nudge_generator"}]
        
        words = user_input_lower.split()

        # 🤯 RANDOM INPUT DETECTION
        if (
            len(user_input_lower) < 5 or
            len(words) == 1 and len(words[0]) < 6
        ):
            return [{"tool": "nudge_generator"}]
        # ==============================
        # 🤖 LLM PLANNING
        # ==============================

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

STRICT RULES:

1. Workout → ONLY workout_generator
2. Diet → ONLY diet_generator
3. Pain/Injury → ONLY recovery_advisor
4. Improve/analyze → insight + workout + diet
5. Casual → nudge_generator

If user asks for progress:
- ONLY use progress_tracker
- DO NOT add any other tool

IMPORTANT:
- Return ONLY JSON array
- NO explanation
- NO duplicate tools
- Always include args for workout_generator

Example:
[
  {{
    "tool": "workout_generator",
    "args": {{
      "focus": "chest",
      "intensity": "low"
    }}
  }}
]
"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
            )

            output = response.choices[0].message.content

            plan = self.safe_parse(output)

            plan = self.validate_plan(plan)

            # ==============================
            # 🚨 STRONG FALLBACK (FINAL GUARD)
            # ==============================

            if not plan:
                if "diet" in user_input_lower:
                    return [{"tool": "diet_generator"}]

                elif "workout" in user_input_lower:
                    return [{
                        "tool": "workout_generator",
                        "args": {"focus": "general", "intensity": "medium"}
                    }]

                elif "progress" in user_input_lower:
                    return [{"tool": "progress_tracker"}]

                else:
                    return [{"tool": "nudge_generator"}]

            return plan

        except Exception as e:
            print("❌ PLANNER ERROR:", str(e))
            return [{"tool": "nudge_generator"}]