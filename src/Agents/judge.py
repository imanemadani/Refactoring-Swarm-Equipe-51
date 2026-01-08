from src.utils.logger_adapter import LoggerAdapter

class JudgeAgent:
    def __init__(self, llm_client, logger):
        self.llm = llm_client
        self.logger = logger

    def judge(self, code):
    
        prompt = """Act like a Python expert and a Tester expert
Run pytest on this Python file and return the result. 
if all tests pass, return "SUCCESS" 
If any test fails, return "FAIL" and include the errors in a structured way. 
Do not make any code modifications. 
Respond clearly so it can be interpreted automatically."""
        
        # Send prompt + code to LLM
        test_result = self.llm.send(prompt, code)
        
        # Log the interaction
        self.logger.log(
            input_prompt=prompt,
            output_response=test_result,
            action_type="DEBUG"
        )
        
        return test_result

