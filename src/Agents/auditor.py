
from src.utils.logger import log_experiment, ActionType
from src.Prompts.Prompts import AUDITOR_PROMPT

class AuditorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def analyze(self, code: str, pylint_output: str = None) -> dict:
        """
        Analyze a Python code snippet and generate a structured fix plan.

        Args:
            code (str): The Python code to analyze.
            pylint_output (str, optional): Pylint output to assist analysis.

        Returns:
            dict: A JSON-structured plan with bugs, syntax errors, logic errors, missing tests, and fix_plan.
        """
        # Combine code + pylint output for context
        input_text = code
        if pylint_output:
            input_text += "\n\n# Pylint output:\n" + pylint_output

        # Send prompt + code to LLM
        response = self.llm.send(AUDITOR_PROMPT, input_text)

        # Log using Quality Manager function
        log_experiment(
            agent_name="Auditor",
            model_used="Gemini",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": AUDITOR_PROMPT,
                "input_code": code,
                "pylint_output": pylint_output,
                "output_response": response
            },
            status="SUCCESS"
        )

        # Convert LLM response to dict if needed (assuming LLM returns JSON string)
        import json
        try:
            plan_json = json.loads(response)
        except Exception as e:
            plan_json = {"error": "Failed to parse LLM response as JSON", "raw_response": response}

        return plan_json
