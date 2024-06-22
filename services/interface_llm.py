from abc import ABCMeta, abstractmethod

class InterfaceLLM(metaclass=ABCMeta):
    "An interface for the LLM class"
    @staticmethod
    @abstractmethod
    def generate_llm_response(context, prompt, model, stream, max_tokens, stop, frequency_penalty, presence_penalty, temperature, top_p):
        "Generate a chat response"