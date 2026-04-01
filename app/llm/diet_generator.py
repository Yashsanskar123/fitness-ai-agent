from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

from app.memory.memory_manager import MemoryManager

load_dotenv()


class DietGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.memory = MemoryManager()

    def generate_diet(self, user_id=1):

        # 🧠 Step 1: Get memory safely
        context = self.memory.build_user_context(user_id) or {}
        user = context.get("user_profile", {}) or {}

        weight = user.get("weight", 65)
        goal = user.get("goal", "general_fitness")
        diet_type = user.get("diet_type", "vegetarian")

        # 🧮 Step 2: Protein logic
        protein_target = round(weight * 1.8)

        # 🧾 Step 3: Prompt
        prompt = f"""
You are a professional Indian fitness nutritionist.

User:
Weight: {weight} kg
Goal: {goal}
Diet Type: {diet_type}

Protein Target: {protein_target}g

Task:
Generate a full day diet plan.

Rules:
- Indian foods only
- High protein
- Split into 4-5 meals
- Mention protein per meal
- Return ONLY JSON

IMPORTANT:
- protein_target must be realistic (around given target)
- NEVER exceed 200g

STRICT RULE:
- DO NOT include explanation
- DO NOT include notes
- DO NOT include text before or after JSON
- ONLY return JSON

Format:
{{
  "total_calories": ...,
  "protein_target": ...,
  "meals": [
    {{
      "meal": "...",
      "items": ["...", "..."],
      "protein": ...
    }}
  ]
}}
"""

        # 🤖 Step 4: LLM call
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )

        output = response.choices[0].message.content

        # =====================================================
        # 🧹 STEP 5: ROBUST JSON PARSING (FIXED PROPERLY)
        # =====================================================

        json_output = None

        try:
            # 🔥 Direct parse
            json_output = json.loads(output)

        except:
            try:
                # 🔥 Clean response
                cleaned = output.strip()
                cleaned = re.sub(r"```json|```", "", cleaned)
                cleaned = re.sub(r",\s*}", "}", cleaned)
                cleaned = re.sub(r",\s*]", "]", cleaned)

                # 🔥 Extract full JSON block
                start = cleaned.find("{")
                end = cleaned.rfind("}") + 1

                if start != -1 and end != -1:
                    json_str = cleaned[start:end]
                    json_output = json.loads(json_str)

            except Exception as e:
                print("❌ JSON PARSE FAILED:", e)
                json_output = None

        # =====================================================
        # 🚨 FINAL SAFETY (FIXED CONDITION)
        # =====================================================

        if not json_output or not isinstance(json_output, dict):
            print("RAW DIET OUTPUT:", output)

            return {
                "total_calories": 2200,
                "protein_target": protein_target,
                "meals": [],
                "note": "Diet generation fallback used"
            }

        # 🔥 Ensure meals key exists
        if "meals" not in json_output or not isinstance(json_output["meals"], list):
            json_output["meals"] = []

        # 🔥 Protein cap safety
        if json_output.get("protein_target", 0) > 200:
            json_output["protein_target"] = protein_target

        return json_output