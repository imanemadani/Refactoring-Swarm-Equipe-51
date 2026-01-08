from .logger import log_experiment, ActionType
# This class acts as a helper to make logging cleaner and standardized for different agents, 
# so they only call LoggerAdapter.log(...) instead of setting up all the log_experiment parameters manually
class LoggerAdapter:
    def __init__(self, agent_name, model_used="fake-llm"):
        self.agent_name = agent_name
        self.model_used = model_used

    def log(self, input_prompt, output_response, action_type, status="SUCCESS"):
        # # Map string action_type to ActionType enum if possible
        # try:
        #     action_enum = ActionType(action_type)
        # except ValueError:
        #     action_enum = action_type  # fallback if it's already a string

        details = {
            "input_prompt": input_prompt,
            "output_response": output_response
        }

        # Call main logger
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_used,
            action=action_type,
            details=details,
            status=status
        )
