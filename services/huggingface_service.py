import os
import argparse
from config import project as config
from services.interface_llm import InterfaceLLM
from huggingface_hub.hf_api import HfFolder
import transformers
import torch


class HuggingFaceService(InterfaceLLM):
    "HuggingFace Service class"
    model = None
    
    def __new__(cls, model):
        cls.model = model
        return cls

    @classmethod
    def generate_llm_response(cls, context, prompt, stream=False, max_tokens=512, stop="<|eot_id|>", frequency_penalty=0, presence_penalty=0, temperature=.7, top_p=.9):

        HF_TOKEN = os.getenv('HF_TOKEN')
        HfFolder.save_token(HF_TOKEN)
        pipeline = transformers.pipeline('text-generation', model=cls.model, model_kwargs={
            "torch_dtype": torch.bfloat16},
            device="cuda"
        )

        messages = [
            {"role": "system", "content": {context}},
            {"role": "user", "content": {prompt}},
        ]

        prompt = pipeline.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        terminators = [
            pipeline.tokenizer.eos_token_id,
            pipeline.tokenizer.convert_tokens_to_ids(stop)
        ]

        outputs = pipeline(
            prompt,
            max_new_tokens=max_tokens,
            eos_token_id=terminators,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
        )

        generated_text = outputs[0]['generated_text'][len(prompt):]
        return generated_text
