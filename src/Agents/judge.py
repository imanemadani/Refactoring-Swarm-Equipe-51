from src.Prompts.Prompts import JUDGE_PROMPT
from src.utils.logger import log_experiment, ActionType
from src.utils.tools.test_tools import run_pytest

class JudgeAgent:
    def __init__(self, llm_client, model_name="gpt-4"):
        self.llm = llm_client
        self.model_name = model_name

    def judge(self, code: str) -> dict:
        # Everything here MUST be indented 4 spaces (one tab)
        prompt = JUDGE_PROMPT
        test_code = self.llm.send(prompt, code)

        # Run pytest safely
        try:
            result = run_pytest({"corrected_code.py": code, "test_code.py": test_code})
        except Exception as e:
            result = {"status": "FAILURE", "details": str(e)}

        status = "SUCCESS" if result.get("all_passed", False) else "FAILURE"

        log_experiment(
            agent_name="Judge",
            model_used=self.model_name,
            action=ActionType.DEBUG,
            details={
                "input_prompt": prompt,
                "input_code": code,
                "output_response": test_code, 
                "sandbox_result": result
            },
            status="SUCCESS"
        )

        return {"status": status, "details": str(result)}