from src.utils.logger_adapter import LoggerAdapter

class FixerAgent:
    def __init__(self, llm_client, logger):
        self.llm = llm_client
        self.logger = logger

    def fix(self, code, plan):
        
        prompt = """Act like a Python expert and analyse this python file and the refactoring plan carefully
reads the plan step by step with no missing detail
modifies the code file by file following the plan and the errors detected 
Respond in a structured and clear way so the changes can be applied automatically."""
        
        # Send prompt + code + plan to LLM
        fixed_code = self.llm.send(prompt, code + "\n\n" + plan)
        
        # Log the interaction
        self.logger.log(
            input_prompt=prompt,
            output_response=fixed_code,
            action_type="FIX"
        )
        
        return fixed_code
