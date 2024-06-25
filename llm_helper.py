from services.llm_service import LLMService
from config import project as config
import json


class LLMHelper:

    @staticmethod
    # TODO actually class context is class name
    def generate_similar_concepts(class_concept, llm, model, log_time):
        # import the prompt config file
        with open(config['prompts']['suggestion']) as f:
            json_prompt = json.load(f)
            context = json_prompt['context']
            prompt = json_prompt['prompt']
            prompt = prompt.replace("{{class_concept}}", class_concept)
            llm_service = LLMService.init_llm(llm, model)
            response = llm_service.generate_llm_response(context=context, prompt=prompt)

            # create a log file to store the class candidate generated
            log_file = open(f"./artifacts/chat_logs/{log_time}.log", "a")
            log_file.write(f">[user]: {prompt}\n>[{llm}]: {response}\n\n\n")
            log_file.close()
            return response

    def generate_cooccurence_concepts(context, llm, model, log_time):
        # import the prompt config file
        with open(config['prompts']['entrypoint']) as f:
            json_prompt = json.load(f)
            prompt = json_prompt['prompt']
            prompt = prompt.replace("{{concept}}", context)
            llm_service = LLMService.init_llm(llm, model)
            response = llm_service.generate_llm_response(context=context, prompt=prompt)

            # create a log file to store the class candidate generated
            log_file = open(f"./artifacts/chat_logs/{log_time}.log", "a")
            log_file.write(f">[user]: {prompt}\n>[{llm}]: {response}\n\n\n")
            log_file.close()
            return response

    def justify_suggestion(class_str, llm, model, log_time):
        with open(config['prompts']['justification']) as f:
            json_prompt = json.load(f)
            prompt = json_prompt['prompt']
            prompt = prompt.replace("{{class}}", class_str)
            llm_service = LLMService.init_llm(llm, model)
            response = llm_service.generate_llm_response(context=class_str, prompt=prompt)

            # create a log file to store the class candidate generated
            log_file = open(f"./artifacts/justification_logs/{log_time}.log", "a")
            log_file.write(f">[user]: {prompt}\n>[{llm}]: {response}\n\n\n")
            log_file.close()
            return response