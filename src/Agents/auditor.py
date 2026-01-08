

from src.utils.logger import log_experiment, ActionType
from src.Prompts.Prompts import AUDITOR_PROMPT

class AuditorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def analyze(self, code):
        prompt = AUDITOR_PROMPT  # load prompt from separate file

        # Send prompt + code to LLM
        response = self.llm.send(prompt, code)

        # Log using Quality Manager function (mandatory)
        log_experiment(
            agent_name="Auditor",
            model_used="Gemini",  # or mock model
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": prompt,
                "output_response": response
            },
            status="SUCCESS"
        )

        return response
