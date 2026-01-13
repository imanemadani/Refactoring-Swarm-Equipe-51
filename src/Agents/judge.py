from src.Prompts.Prompts import JUDGE_PROMPT
from src.utils.logger import log_experiment, ActionType
from sandbox import run_in_sandbox  # hypothetical utility
from src.utils.tools.test_tools import run_pytest  # your function for generating run_pytest tests

class JudgeAgent:
    def __init__(self, llm_client, model_name="gpt-4"):
        self.llm = llm_client
        self.model_name = model_name

    def judge(self, code: str) -> str:
        """
        Generate run_pytest-based tests for the corrected code, put them in a sandbox,
        run them, and return only 'SUCCESS' or 'FAILURE'.

        Args:
            code (str): Corrected Python code from FixerAgent.

        Returns:
            str: 'SUCCESS' if all tests pass, 'FAILURE' if any test fails.
        """
        prompt = JUDGE_PROMPT

        # Step 1: Ask LLM to generate tests using ptest
        test_code = self.llm.send(prompt, code)

        # Step 2: Place the tests in the sandbox with the corrected code
        # run_in_sandbox is a utility that executes code safely
        try:
            result = run_in_sandbox(
                code_files={"corrected_code.py": code, "test_code.py": test_code},
                test_runner=run_pytest  # this will execute run_pytest on test_code.py
            )
        except Exception as e:
            result = "FAILURE"

        # Step 3: Determine success/failure based on run_pytest results
        if isinstance(result, dict):
            # If ptest returns structured info
            test_status = "SUCCESS" if result.get("all_passed", False) else "FAILURE"
        else:
            # Otherwise, fallback
            test_status = "FAILURE" if result != "SUCCESS" else "SUCCESS"

        # Step 4: Log the operation
        log_experiment(
            agent_name="Judge",
            model_used=self.model_name,
            action=ActionType.DEBUG,
            details={
                "input_prompt": prompt,
                "input_code": code,
                "generated_tests": test_code,
                "sandbox_result": result
            },
            status="SUCCESS"
        )

        return {"status": test_status, "details": str(result)}
