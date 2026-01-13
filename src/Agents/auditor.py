from src.utils.logger import log_experiment, ActionType
from src.Prompts.Prompts import AUDITOR_PROMPT  # <--- MAKE SURE THIS LINE IS HERE
import json

class AuditorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
    # CHECK THIS LINE BELOW - Make sure it says 'analyze'
    def analyze(self, code: str, pylint_output: str = None) -> dict:
        input_text = code
        if pylint_output:
            input_text += "\n\n# Pylint output:\n" + pylint_output

        response = self.llm.send(AUDITOR_PROMPT, input_text)

        # 1. Clean markdown for the JSON parser
        cleaned_response = response.replace("```json", "").replace("```", "").strip()

        # 2. LOGGING: Ensure these match your TP requirements
        log_experiment(
            agent_name="Auditor",
            model_used="Gemini",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": AUDITOR_PROMPT,
                "input_code": code,
                "pylint_output": pylint_output,
                "output_response": response # Make sure this key is here
            },
            status="SUCCESS"
        )

        # 3. Parse JSON
        try:
            plan_json = json.loads(cleaned_response)
        except Exception:
            plan_json = {"error": "Failed to parse LLM response", "raw_response": response}

        return plan_json