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

        # 🧠 Step 1: Get memory
        context = self.memory.build_user_context(user_id)
        user = context["user_profile"]

        weight = user["weight"]
        goal = user["goal"]
        diet_type = user["diet_type"]

        # 🧮 Step 2: Basic protein logic
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

                # 🧹 Step 5: Clean JSON (ROBUST)
        json_output = None

        try:
            json_output = json.loads(output)

        except:
            output = output.strip()
            output = re.sub(r"```json|```", "", output)

            match = re.search(r"\{.*\}", output, re.DOTALL)

            if match:
                json_str = match.group()

                json_str = re.sub(r",\s*}", "}", json_str)
                json_str = re.sub(r",\s*]", "]", json_str)

                try:
                    json_output = json.loads(json_str)
                except:
                    pass

        # 🚨 FINAL SAFETY
        if not json_output:
            print("RAW DIET OUTPUT:", output)

            return {
                "total_calories": 2200,
                "protein_target": protein_target,
                "meals": [],
                "note": "Could Not fully generate diet, try again"
            }

        # 🔥 HARD PROTEIN CAP
        if json_output.get("protein_target", 0) > 200:
            json_output["protein_target"] = protein_target

        return json_output