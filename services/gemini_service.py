import os
import json
import time
from config import project as config
from dotenv import load_dotenv
from services.interface_llm import InterfaceLLM
from datetime import datetime, timedelta
import google.generativeai as genai

load_dotenv()

class GeminiService(InterfaceLLM):
    "Gemini Service class"
    model = None
    requests_per_minute = config['general']['requests_per_minute']
    api_key = os.getenv("GEMINI_API_KEY")
    interval = 60.0 / requests_per_minute
    start_time = datetime.now()
    requests_count = 0

    def __new__(cls, model):
        cls.model = model
        return cls

    @classmethod
    def generate_llm_response(cls, context, prompt, stream=False, max_tokens=2048, stop=None, frequency_penalty=0, presence_penalty=0, temperature=.7, top_p=.95):
        genai.configure(api_key=cls.api_key)
        # The Gemini 1.5 models are versatile and work with both text-only and multi modal prompts
        print(f"Request count: {cls.requests_count}")
        
        generation_config = genai.GenerationConfig(
            candidate_count=1,
            max_output_tokens=max_tokens,
            temperature=temperature
        )

        model = genai.GenerativeModel(cls.model)

        response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
        cls.requests_count += 1
        # sleep 10 seconds
        time.sleep(10)
        return response.candidates[0].content.parts[0].text
            
            # Calculate how long to sleep until the next minute
        #     elapsed_time = datetime.now() - cls.
        #     if elapsed_time < timedelta(minutes=1):
        #         time_to_sleep = timedelta(minutes=1) - elapsed_time
        #         print(f"Sleeping for {time_to_sleep.total_seconds()} seconds until the next minute...")
        #         time.sleep(time_to_sleep.total_seconds())
        #         return response.candidates[0].content.parts[0].text
        #         # return response.text
        #     else:
        #         cls.start_time = datetime.now()
        #         cls.requests_count = 0
        #         return response.candidates[0].content.parts[0].text
        #         # return response.text
        # else:
        #     print("Rate limit reached. Please wait until the next minute to make another request.")
        #     return "Rate limit reached. Please wait until the next minute to make another request."