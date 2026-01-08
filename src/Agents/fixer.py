from src.Prompts.Prompts import FIXER_PROMPT
from src.utils.logger import log_experiment, ActionType

class FixerAgent:
    def __init__(self, llm_client, model_name="gpt-4"):
        self.llm = llm_client
        self.model_name = model_name

    def fix(self, code, plan):
        prompt = FIXER_PROMPT

        # Send prompt + code + plan to LLM
        fixed_code = self.llm.send(prompt, code + "\n\n" + plan)

        # Log using Quality Manager function
        log_experiment(
            agent_name="Fixer",
            model_used=self.model_name,
            action=ActionType.FIX,
            details={
                "input_prompt": prompt,
                "output_response": fixed_code
            },
            status="SUCCESS"
        )

        return fixed_code
