import os
from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()


class GeminiClient:
    """
    Maroua:)Toolsmith utility:
    - Wraps Gemini API access
    - Exposes a single `send()` method
    - Can be mocked or real without changing agents // for now mocked later when Gemini API is available real API calls
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")  # Gemini API key

        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. "
                "Make sure it exists in the .env file."
            )

    def send(self, prompt: str, code: str) -> str:
        """
        This method is called by:
        - AuditorAgent
        - FixerAgent
        - JudgeAgent

        For now: MOCKED response
        Later: real Gemini API call
        """

        # SECURITY: never print the key
        print("[GeminiClient] Gemini API called (mock mode)")

        # MOCK RESPONSE (temporary)
        return (
            "MOCK GEMINI RESPONSE:\n"
            "- Fix indentation\n"
            "- Rename function to snake_case\n"
            "- Add docstring\n"
            "- Replace print with logging"
        )
