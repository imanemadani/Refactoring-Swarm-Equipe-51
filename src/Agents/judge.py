from src.Prompts.Prompts import JUDGE_PROMPT
from src.utils.logger import log_experiment, ActionType

class JudgeAgent:
    def __init__(self, llm_client, model_name="gpt-4"):
        self.llm = llm_client
        self.model_name = model_name  # optional: allow multiple models

    def judge(self, code):
        prompt = JUDGE_PROMPT  # load prompt from separate file

        # Send prompt + code to LLM
        test_result = self.llm.send(prompt, code)

        # Log using Quality Manager function (mandatory)
        log_experiment(
            agent_name="Judge",
            model_used=self.model_name,
            action=ActionType.DEBUG,
            details={
                "input_prompt": prompt,
                "output_response": test_result
            },
            status="SUCCESS"
        )

        return test_result
