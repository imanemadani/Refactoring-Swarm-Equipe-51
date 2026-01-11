from src.Prompts.Prompts import FIXER_PROMPT
from src.utils.logger import log_experiment, ActionType
import json

class FixerAgent:
    def __init__(self, llm_client, model_name="gpt-4"):
        self.llm = llm_client
        self.model_name = model_name

    def fix(self, code: str, plan: dict) -> str:
        """
        Apply a structured fix plan to Python code using the LLM.

        Args:
            code (str): The Python code to fix.
            plan (dict): JSON-structured fix plan from AuditorAgent.

        Returns:
            str: Corrected Python code.
        """
        prompt = FIXER_PROMPT

        # Ensure plan is a JSON string
        plan_str = json.dumps(plan, indent=2)

        # Combine code + plan for LLM input
        input_text = f"{code}\n\n# Fix plan:\n{plan_str}"

        # Send prompt + input to LLM
        fixed_code = self.llm.send(prompt, input_text)

        # Log using Quality Manager
        log_experiment(
            agent_name="Fixer",
            model_used=self.model_name,
            action=ActionType.FIX,
            details={
                "input_prompt": prompt,
                "input_code": code,
                "fix_plan": plan,
                "output_response": fixed_code
            },
            status="SUCCESS"
        )

        return fixed_code
