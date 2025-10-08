'''Wrapper around a local language model server.

This client provides a minimal abstraction layer for sending chat requests to
an OpenAI-compatible local server such as Ollama or LM Studio. It reads
configuration from environment variables at initialisation time: LLM_BASE_URL
points at the local API endpoint and LLM_MODEL names the model to use.

If the OpenAI Python library is installed, the client uses it; otherwise it
falls back to a simple HTTP POST via urllib.request. In both cases the
interface is the same: call chat(prompt, **kwargs) and receive the model’s
response as a string.
'''

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, Optional

try:
    import openai  # type: ignore
except ImportError:
    openai = None  # type: ignore

class LLMClient:
    '''Client for interacting with a local LLM server.'''

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.base_url = base_url or os.environ.get('LLM_BASE_URL', 'http://localhost:11434/v1')
        self.model = model or os.environ.get('LLM_MODEL', 'mistral:7b')
        self.api_key = os.environ.get('LLM_API_KEY', 'dummy')
        if openai is not None:
            # Configure OpenAI client to point at local server
            openai.base_url = self.base_url
            openai.api_key = self.api_key

    def chat(self, prompt: str, temperature: float = 0.2, max_tokens: int = 2048) -> str:
        '''Send a chat request to the local LLM and return the response text.

        :param prompt: The prompt string to send.
        :param temperature: Sampling temperature.
        :param max_tokens: Maximum number of tokens in the response.
        :returns: The assistant’s reply as a string.
        '''
        if openai is not None:
            completion = openai.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return completion.choices[0].message.content

        # Fallback to HTTP
        url = f'{self.base_url}/chat/completions'
        data: Dict[str, Any] = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.api_key}'},
        )
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            payload = json.loads(body)
        # The structure matches the OpenAI API.
        try:
            return payload['choices'][0]['message']['content']
        except Exception:
            return ''
