
class FakeLLM:
    """
    Simulates an AI LLM response for testing the self-healing loop and logging.
    """
    def send(self, prompt, code):
        # Always returns the same fake response
        return "SIMULATED RESPONSE"
