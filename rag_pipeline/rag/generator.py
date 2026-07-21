"""
rag/generator.py — calls Gemma 4 running locally via Ollama's REST API.

No API key, no cost — this hits your own machine's Ollama server.
Make sure Ollama is running and the model is pulled first:

    ollama pull gemma4:e4b
    ollama serve      # usually already running as a background service
"""

import requests

import config


class OllamaGenerator:
    def __init__(self, model=None, base_url=None):
        self.model = model or config.OLLAMA_MODEL
        self.base_url = base_url or config.OLLAMA_BASE_URL

    def generate(self, system_prompt, user_message, temperature=None, num_ctx=None):
        """
        Send a chat-style request to Ollama and return the model's reply text.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else config.OLLAMA_TEMPERATURE,
                "num_ctx": num_ctx or config.OLLAMA_NUM_CTX,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Could not reach Ollama at "
                f"{self.base_url}. Is it running? Try: `ollama serve` "
                f"and make sure `{self.model}` has been pulled."
            )

        data = response.json()
        return data.get("message", {}).get("content", "").strip()
