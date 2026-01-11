import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class LlamaClient:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = os.getenv("OPENROUTER_API_KEY")

    def send(self, prompt: str, code: str) -> str:
        print(f"🦙 OpenRouter is processing...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000", # Optional but good for OpenRouter
            "X-Title": "Refactoring Swarm"
        }

        payload = {
            "model": "google/gemini-2.0-flash-001", 
            "messages": [
                {"role": "user", "content": f"{prompt}\n\nCODE:\n{code}"}
            ]
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"OPENROUTER_ERROR: {response.status_code} - {response.text}"
        except Exception as e:
            return f"CONNECTION_ERROR: {e}"