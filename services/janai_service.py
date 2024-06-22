
from services.interface_llm import InterfaceLLM
import requests

class JanAIService(InterfaceLLM):
    "JanAI Service class"
    model = None
    
    def __new__(cls, model):
        cls.model = model
        return cls

    @classmethod
    def generate_llm_response(cls, context, prompt, stream=False, max_tokens=2048, stop=None, frequency_penalty=0, presence_penalty=0, temperature=.7, top_p=.95):
        url = "http://localhost:1337/v1/chat/completions"

        payload = {
            "messages": [
                {
                    "content": context,
                    "role": "system"
                },
                {
                    "content": prompt,
                    "role": "user"
                },
            ],
            "model": cls.model,
            "stream": stream,
            "max_tokens": max_tokens,
            "stop": stop,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "temperature": temperature,
            "top_p": top_p
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        content = result['choices'][0]['message']['content']

        return content