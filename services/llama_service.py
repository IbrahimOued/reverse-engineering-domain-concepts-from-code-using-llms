import os
import argparse
from config import project as config
from services.interface_llm import InterfaceLLM
from huggingface_hub.hf_api import HfFolder
import transformers
import torch


class LlamaService(InterfaceLLM):
    def generate_llm_response(context, class_context, model, stream, max_tokens, stop, frequency_penalty, presence_penalty, temperature, top_p):

        HF_TOKEN = os.getenv('HF_TOKEN')
        HfFolder.save_token(HF_TOKEN)
        pipeline = transformers.pipeline('text-generation', model=model, model_kwargs={
            "torch_dtype": torch.bfloat16},
            device="cuda"
        )

        messages = [
            {"role": "system", "content": {context}},
            {"role": "user", "content": {class_context}},
        ]

        prompt = pipeline.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        terminators = [
            pipeline.tokenizer.eos_token_id,
            pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = pipeline(
            prompt,
            max_new_tokens=max_tokens,
            eos_token_id=terminators,
            do_sample=True,
            temperature=temperature,
            top_p=.9,
        )

        generated_text = outputs[0]['generated_text'][len(prompt):]
        return generated_text
