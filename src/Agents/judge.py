import os
from src.Prompts.Prompts import JUDGE_PROMPT
from src.utils.logger import log_experiment, ActionType
from src.utils.tools.test_tools import run_pytest

class JudgeAgent:
    def __init__(self, llm_client, model_name="gpt-4"):
        self.llm = llm_client
        self.model_name = model_name

    def judge(self, code: str) -> dict:
        prompt = JUDGE_PROMPT
        # 1. Get test code from LLM
        test_code_raw = self.llm.send(prompt, code)
        
        # 2. Clean the string (remove ```python etc)
        test_code = test_code_raw.replace("```python", "").replace("```", "").strip()

        # 3. Path to your sandbox
        sandbox_dir = "./sandbox/workspace"
        os.makedirs(sandbox_dir, exist_ok=True)

        # 4. Write the code and the tests into the sandbox folder
        with open(os.path.join(sandbox_dir, "test_code.py"), "w", encoding="utf-8") as f:
            f.write(test_code)

        # 5. Run pytest on the WHOLE sandbox directory
        try:
            # Now we pass the string path as your function expects!
            result = run_pytest(sandbox_dir)
        except Exception as e:
            result = {"success": False, "details": str(e)}

        # 6. Map the result to your status
        # Note: Your function returns "success", the orchestrator looks for "all_passed"
        all_passed = result.get("success", False)
        status = "SUCCESS" if all_passed else "FAILURE"

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

        # Return a dictionary that includes all_passed so the main loop can read it
        return {"status": status, "all_passed": all_passed, "details": str(result)}