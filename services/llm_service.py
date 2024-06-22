import os
import requests
from services.interface_llm import InterfaceLLM
from services.gemini_service import GeminiService
from services.janai_service import JanAIService
from services.openai_service import OpenAIService 
from services.llama_service import LlamaService

class LLMService(InterfaceLLM):

    @staticmethod
    def init_llm(service, model):
        if service == "openai":
            return OpenAIService(model)
        elif service == "gemini":
            return GeminiService(model)
        elif service == "janai":
            return JanAIService(model)
        elif service == "llama":
            return LlamaService(model)