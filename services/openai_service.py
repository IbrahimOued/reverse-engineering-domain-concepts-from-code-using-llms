
from services.interface_llm import InterfaceLLM


class OpenAIService(InterfaceLLM):
    def generate_chat_response(context, prompt, model, stream, max_tokens, stop, frequency_penalty, presence_penalty, temperature, top_p):
        "OpenAI Service class"
        assert "Not implemented yet"