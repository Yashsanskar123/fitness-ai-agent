from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

from app.memory.memory_manager import MemoryManager
from app.rag.retriever import Retriever

load_dotenv()


class WorkoutGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.memory = MemoryManager()
        self.retriever = Retriever()

    # 🔥 SAFE RANGE FIX FUNCTION (NO CRASH EVER)
    def fix_reps_ranges(self, text):
        def replacer(match):
            start = match.group(1)
            end = match.group(2)
            return f'"{start}-{end}"'
        return re.sub(r'(\d+)\s*-\s*(\d+)', replacer, text)

    def generate_workout(self, user_id=1, user_input="", focus=None, intensity=None):

        # 🧠 Step 1: Get memory context
        context = self.memory.build_user_context(user_id)

        # 🔍 Step 2: Retrieve exercises
        retrieved_exercises = self.retriever.retrieve(user_input)

        # 🧾 Step 3: Build prompt
        prompt = f"""
You are a professional fitness coach.

User Profile:
{context['user_profile']}

User Injuries:
{context.get('injuries', [])}

IMPORTANT:
- Avoid exercises that can worsen injuries
- Suggest safe alternatives
- Do not include risky movements

Recent Workouts:
{context['recent_workouts']}

Available Exercises:
{retrieved_exercises}

Focus: {focus if focus else "general"}
Intensity: {intensity if intensity else "medium"}

Task:
Generate ONLY ONE workout plan for TODAY.

STRICT RULES:
- Return ONLY ONE JSON object
- DO NOT return multiple days
- DO NOT return multiple JSON objects
- DO NOT generate weekly plan

IMPORTANT:
- Return ONLY valid JSON
- DO NOT include explanations
- DO NOT include notes outside JSON
- "reps" must ALWAYS be a string (e.g., "8-12")
- "day" must be a simple string like "Chest Day"
- DO NOT return malformed strings

Format:
{{
  "day": "...",
  "exercises": [
    {{
      "name": "...",
      "sets": ...,
      "reps": "..."
    }}
  ]
}}
"""

        # 🤖 Step 4: Call LLM
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )

        output = response.choices[0].message.content

        # 🧹 Step 5: Clean JSON (ULTRA ROBUST)
        json_output = None

        try:
            json_output = json.loads(output)

        except:
            output = output.strip()
            output = re.sub(r"```json|```", "", output)

            matches = re.findall(r"\{[^{}]*\}", output, re.DOTALL)

            if matches:
                json_str = matches[0]  # ✅ FIRST VALID JSON ONLY

                # 🔥 SAFE RANGE FIX
                json_str = self.fix_reps_ranges(json_str)

                # 🔥 FIX DOUBLE QUOTES
                json_str = re.sub(r'""(\d+-\d+)""', r'"\1"', json_str)
                json_str = re.sub(r'"{2,}', '"', json_str)

                # 🔥 REMOVE TRAILING COMMAS
                json_str = re.sub(r",\s*}", "}", json_str)
                json_str = re.sub(r",\s*]", "]", json_str)

                try:
                    json_output = json.loads(json_str)
                except:
                    print("❌ BROKEN JSON:", json_str)

        # 🚨 FINAL SAFETY (NEVER BREAK AGENT)
        if not json_output:
            return {
                "day": "Workout Day",
                "exercises": [],
                "note": "Could not generate structured workout. Try again."
            }

        # 🧠 FINAL CLEANUP
        for ex in json_output.get("exercises", []):

            # 🔧 Fix reps int → string
            if isinstance(ex.get("reps"), int):
                ex["reps"] = str(ex["reps"])

            # 🔧 Fix wrong keys
            if "namee" in ex:
                ex["name"] = ex.pop("namee")
            if "name'" in ex:
                ex["name"] = ex.pop("name'")

            # 🔧 Fix typos
            if "name" in ex:
                ex["name"] = ex["name"].replace("BBench", "Bench").replace("BBarbell", "Barbell")

        return json_output
    
    def generate(self, prompt: str):
        """
        🔥 Generic LLM call for decision making (used by AdaptiveEngine)
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a fitness coach AI."},
                    {"role": "user", "content": prompt}
                ],
            )

            output = response.choices[0].message.content.strip()

            print("🤖 LLM RAW RESPONSE:", output)  # DEBUG

            return output

        except Exception as e:
            print("❌ LLM GENERATE ERROR:", str(e))
            return "maintain"  # safe fallback