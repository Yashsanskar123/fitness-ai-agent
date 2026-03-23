class InjuryEngine:

    def __init__(self, memory_manager=None, llm=None):
        self.memory = memory_manager
        self.llm = llm

    def detect_injury(self, user_input, user_id=1):
        """
        Detect injury from user input using LLM
        """

        if not self.llm:
            return None

        prompt = f"""
You are a fitness injury detection assistant.

Analyze the user input and detect if there is any injury.

User input:
"{user_input}"

Return ONLY JSON:

{{
  "injury_detected": true/false,
  "injury_type": "...",
  "severity": "mild/moderate/severe",
  "notes": "short description"
}}

Rules:
- Do NOT include comments (//)
- Output strictly valid JSON

If no injury → return:
{{ "injury_detected": false }}
"""

        try:
            response = self.llm.generate(prompt)

            import json
            import re

            # ---------------------------
            # 🔧 CLEAN RESPONSE
            # ---------------------------
            response = response.strip()
            response = re.sub(r"```json|```", "", response)

            # 🔥 remove inline comments BEFORE parsing
            response = re.sub(r"//.*", "", response)

            # ---------------------------
            # 🔍 EXTRACT JSON
            # ---------------------------
            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                json_str = match.group(0)

                try:
                    data = json.loads(json_str)
                except Exception as e:
                    print("⚠️ JSON parse failed:", json_str)
                    return {"injury_detected": False}

                # ---------------------------
                # 🧠 PROCESS DATA
                # ---------------------------
                if data.get("injury_detected"):

                    injury_type = data.get("injury_type", "unknown")

                    # 🔥 NORMALIZE SEVERITY
                    severity = data.get("severity", "moderate").lower()

                    if "mild" in severity:
                        severity = "mild"
                    elif "severe" in severity:
                        severity = "severe"
                    else:
                        severity = "moderate"

                    notes = data.get("notes", "")

                    # 🔄 update cleaned values
                    data["severity"] = severity
                    data["injury_type"] = injury_type

                    # ---------------------------
                    # 💾 SAVE TO MEMORY
                    # ---------------------------
                    if self.memory:
                        self.memory.save_injury(
                            user_id=user_id,
                            injury_type=injury_type,
                            severity=severity,
                            notes=notes
                        )

                    print("🩹 Injury detected:", data)

                    return data

            return {"injury_detected": False}

        except Exception as e:
            print("❌ Injury detection error:", str(e))
            return {"injury_detected": False}