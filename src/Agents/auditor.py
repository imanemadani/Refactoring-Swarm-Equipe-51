

# from src.utils.logger import Logger  # make sure logger is imported at the top
from src.utils.logger_adapter import LoggerAdapter
from src.utils.logger import ActionType

class AuditorAgent:
    def __init__(self, llm_client, logger):
        self.llm = llm_client
        self.logger = logger

    def analyze(self, code):
        prompt = """Act like a Python expert and analyze this Python file carefully.
- Read the code and identify:
  - Bugs
  - Syntax errors
  - Logical errors
  - Missing tests
Respond in a comprehensive and structured way so the Fixer agent can clearly follow your instructions.
"""
        # Send prompt + code to LLM
        response = self.llm.send(prompt, code)
        
        # Log the interaction
        self.logger.log(
            input_prompt=prompt,
            output_response=response,
            action_type=ActionType.ANALYSIS 
        )
        
        return response