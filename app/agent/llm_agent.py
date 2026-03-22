from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

from app.llm.workout_generator import WorkoutGenerator
from app.llm.diet_generator import DietGenerator
from app.memory.memory_manager import MemoryManager
from app.agent.adaptive_engine import AdaptiveEngine
from app.agent.insight_engine import InsightEngine
from app.agent.nudge_engine import NudgeEngine
from app.agent.tool_registry import ToolRegistry
from app.agent.reflection_engine import ReflectionEngine

load_dotenv()


class LLMAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Tools
        self.workout_gen = WorkoutGenerator()
        self.diet_gen = DietGenerator()
        self.memory = MemoryManager()
        self.adaptive = AdaptiveEngine()
        self.insight = InsightEngine()
        self.nudge = NudgeEngine()
        self.registry = ToolRegistry()

        # Register tools
        self.registry.register("workout_generator", self.workout_gen.generate_workout)
        self.registry.register("diet_generator", self.diet_gen.generate_diet)
        self.registry.register("progress_tracker", self.memory.get_progress_history)
        self.registry.register("recovery_advisor", self.recovery_tool)
        self.registry.register("insight_generator", self.insight.generate_insights)
        self.registry.register("nudge_generator", self.nudge.generate_nudges)

        # Allowed tools
        self.VALID_TOOLS = {
            "workout_generator",
            "diet_generator",
            "progress_tracker",
            "recovery_advisor",
            "insight_generator",
            "nudge_generator"
        }

    # ---------------- JSON SAFE PARSER ---------------- #

    def safe_parse_json(self, output: str):
        try:
            return json.loads(output)
        except Exception as e:
            print("❌ JSON PARSE ERROR (raw):", output)

            output = output.strip()
            output = re.sub(r"```json|```", "", output)

            match = re.search(r"\{.*\}", output, re.DOTALL)
            if match:
                json_str = match.group()

                # remove trailing commas
                json_str = re.sub(r",\s*}", "}", json_str)
                json_str = re.sub(r",\s*]", "]", json_str)

                try:
                    return json.loads(json_str)
                except Exception as e:
                    print("❌ JSON STILL BROKEN:", json_str)
                    return None

            return None

    # ---------------- DECISION ENGINE ---------------- #

    def decide_action(self, user_input, context):

        prompt = f"""
You are an intelligent fitness AI agent.

User Input:
{user_input}

User Context:
{context}

Available Tools:

1. workout_generator → use when user asks for workout, exercise plan, gym routine
2. diet_generator → use when user asks about food, diet, meals, nutrition
3. progress_tracker → use when user asks for logs or history
4. recovery_advisor → use when user mentions pain, soreness, fatigue
5. insight_generator → use ONLY when user asks to analyze progress or trends
6. nudge_generator → use for daily advice, motivation, reminders

STRICT RULES:
- "advice", "today", "what should I do" → nudge_generator
- "analyze", "progress report" → insight_generator
- DO NOT confuse between insight and nudge
- casual/unclear -> nudge_generator

IMPORTANT:
- ONLY choose from available tools
- DO NOT invent tool names
- Be precise

ARGS RULES:
- workout_generator → may include "focus" (chest, legs, full body), "intensity" (low, medium, high)
- diet_generator → no args needed
- progress_tracker → no args
- recovery_advisor → no args
- insight_generator → no args
- nudge_generator → no args

STRICT:
- Output ONLY JSON
- DO NOT explain anything
- DO NOT add extra text
- DO NOT wrap in markdown

focus MUST be one of:
["chest", "legs", "back", "full body", "arms", "shoulders"]

Return ONLY JSON:
{{
  "tool": "...",
  "args": {{
    "focus": "...",
    "intensity": "..."
  }},
  "reason": "..."
}}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  
                messages=[{"role": "user", "content": prompt}],
            )

            output = response.choices[0].message.content
            decision = self.safe_parse_json(output)

            return decision

        except Exception as e:
            print("❌ LLM ERROR:", str(e))
            return None

    def recovery_tool(self, user_id=1):
        return {
            "advice": "Take rest, hydrate well, sleep properly, and do light stretching."
        }

    # ---------------- MAIN AGENT ---------------- #

    def run(self, user_input, user_id=1):

        print("📥 USER INPUT:", user_input)

        try:
            # 🧠 Get context
            context = self.memory.build_user_context(user_id)
            print("🧠 CONTEXT:", context)

            # 🤖 Decide
            decision = self.decide_action(user_input, context)
            print("🧠 RAW DECISION:", decision)

            # 🚨 Validate decision
            if not decision or decision.get("tool") not in self.VALID_TOOLS:
                print("⚠️ Invalid tool → fallback")

                user_input_lower = user_input.lower()

                if "diet" in user_input_lower or "eat" in user_input_lower:
                    tool = "diet_generator"

                elif "workout" in user_input_lower or "exercise" in user_input_lower:
                    tool = "workout_generator"

                elif "progress" in user_input_lower or "weight" in user_input_lower:
                    tool = "progress_tracker"

                elif "tired" in user_input_lower or "sore" in user_input_lower:
                    tool = "recovery_advisor"

                else:
                    return {
                        "message": "I can help with workouts, diet, recovery, and progress tracking."
                    }

            else:
                tool = decision["tool"]
                args = decision.get("args", {})

            print("✅ FINAL TOOL:", tool)

            # ---------------- TOOL EXECUTION ---------------- #

            try:
                tool_func = self.registry.get(tool)

                if not tool_func:
                    return {"error": f"Tool '{tool}' not found"}

                if tool == "workout_generator":
                    # result = tool_func(user_id, user_input)
                    args["user_id"] = user_id

                    if tool == "workout_generator":
                        args["user_input"] = user_input
                    result = tool_func(**args)

                    insights = self.adaptive.analyze(context)
                    result = self.adaptive.modify_workout(result, insights)
                    result["coach_tip"] = self.adaptive.generate_coaching_tip(insights)

                elif tool == "diet_generator":
                    result = tool_func(user_id)

                elif tool == "progress_tracker":
                    result = tool_func(user_id)

                elif tool == "insight_generator":
                    result = {"insights": tool_func(context)}

                elif tool == "nudge_generator":
                    result = {"nudges": tool_func(context)}

                elif tool == "recovery_advisor":
                    result = tool_func(user_id)

                else:
                    result = {"error": "Unhandled tool"}

                print("⚙️ TOOL RESULT:", result)

                return result

            except Exception as e:
                print("❌ TOOL ERROR:", str(e))
                return {"error": "Tool execution failed"}

        except Exception as e:
            print("❌ AGENT ERROR:", str(e))
            return {
                "error": "Something went wrong while processing your request"
            }