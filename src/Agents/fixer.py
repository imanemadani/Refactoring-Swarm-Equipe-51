from src.Prompts.Prompts import FIXER_PROMPT
from src.utils.logger import log_experiment, ActionType
import json


class FixerAgent:
    def __init__(self, llm_client, model_name="gpt-4"):
        self.llm = llm_client
        self.model_name = model_name


    def fix(self, code: str, plan) -> str:
        prompt = FIXER_PROMPT


        if isinstance(plan, dict):
            plan_str = json.dumps(plan, indent=2)
        else:
            plan_str = str(plan)


        # Clean markdown from plan
        plan_str = plan_str.replace("```json", "").replace("```", "").strip()


        input_text = f"{code}\n\n# Fix plan:\n{plan_str}"
        fixed_code = self.llm.send(prompt, input_text)


        # Clean markdown from fixed code
        if isinstance(fixed_code, str):
            fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()


        # SAFETY: fallback to original code if invalid
        if not fixed_code or "OPENROUTER_ERROR" in fixed_code or len(fixed_code) < 1:
            return code


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