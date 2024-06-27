import datetime
import re
from config import project as config
import argparse
from utils.extract_signatures import create_signatures_dataframe
from utils.get_project_paths import get_folder_paths
from seed_detector.seed_detector import detect_project_seed
from preprocessing.code_preprocessor import CodePreprocessor
from custom_models.custom_embedder import CustomEmbedder
import pandas as pd
from model.class_component import ClassCategory, ClassComponent, AttributeNode, MethodNode
from llm_helper import LLMHelper


def main():
    repositories_folder = config['general']['repositories_folder']
    repositories_dict = get_folder_paths(repositories_folder)
    preprocessor = CodePreprocessor()
    custom_embedder = CustomEmbedder(model=config['models']['embedder'])
    llm = config['models']['llm']
    model = config['models']['model']

    # This is for all the projects
    for project_name, project_path in repositories_dict.items():
        sig_dataframe = create_signatures_dataframe(project_path=project_path)

        # create an empty dataframe
        df = pd.DataFrame(columns=['class_name', 'class_context', 'class_similarity', 'llm_evaluation'])
        # creating a logging dataframe
        log_df = pd.DataFrame(columns=['list_of_given_concepts','concepts_suggested_by_llm', 'closest_class', 'cosine_similarity', 'class_classification_similarity_based', 'llm_auto_classification', 'll_auto_eval_score'])
        
        
        # create a list of element of type ClassComponent
        project_class_components : dict[str, ClassComponent] = {}

        for class_name in sig_dataframe.class_name.unique().tolist():
            classname_tokens = preprocessor.tokenize_class_name(class_name)
            current_class = ClassComponent(class_name=class_name, class_name_tokens=classname_tokens, class_attributes=[], class_methods=[])

            # TODO: Only processing the class name for now
            # for attribute in sig_dataframe.class_attributes.where(sig_dataframe.class_name == class_name).dropna().to_list()[0]:
            #     attr_tokens = preprocessor.tokenize_attributes_name(attribute)
            #     current_class.class_attributes.append(AttributeNode(attribute, attr_tokens))

            # # Methods preprocessing
            # for method_name in sig_dataframe.method_name.where(sig_dataframe.class_name == class_name).dropna().to_list():
            #     method_tokens = preprocessor.tokenize_method_name(method_name)
            #     if len(method_tokens) > 0:
            #         current_class.class_methods.append(MethodNode(method_name, method_tokens))

            # summary text with class name, class attributes and class methods
            df = pd.concat([df, pd.DataFrame({'class_name': [class_name], 'class_context': [current_class.__str__()]})])
            # print(f"Class {class_name} processed successfully...\n")
            project_class_components[class_name] = current_class
        
        # TODO: Using only the most likely domain class at this point, will use the pairs later
        # This is where the entry point loctaor will come into play
        most_likely_domain_class, second_most_likely_domain_class = detect_project_seed(custom_embedder, project_name, project_class_components)
        print(f"Most likely domain class: {most_likely_domain_class}\n")
        most_likely_domain_components = project_class_components[most_likely_domain_class]
        # delete the entrypoint class from the dictionary and the dataframe
        del project_class_components[most_likely_domain_class]
        df = df[df.class_name != most_likely_domain_class]

        # iteration through the classes to compare the similarity
        i = 1
        domain_context = most_likely_domain_components.__str__()
        classification_df = pd.DataFrame(columns=['class_name', 'class_classification', 'class_similarity'])
        # log the prompt and response
        log_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        suggested_concepts = ""
        # start the uml-ifaication
        plantuml_file = open(f"artifacts/class_diagrams/{project_name}.puml", "a")
        plantuml_file.write(f"@startuml\n")
        while len(project_class_components) > 0:
            # for the 1st iteration, the entrypoint prompt will be used
            if i == 1: 
                # use the entrypoint json file to get the domain context
                suggested_concepts = LLMHelper.generate_similar_concepts(domain_context, llm, model, log_time)

            print(f"Starting iteration {i}...")
            # Should follow a particular template to ease comparison
            suggested_concepts = LLMHelper.generate_cooccurence_concepts(domain_context, llm, model, log_time)
            df['cosine_similarity'] = df['class_name'].apply(lambda class_name: custom_embedder.calculate_similarity(class_name, suggested_concepts))
            classname_with_highest_similarity = df[df.cosine_similarity == df.cosine_similarity.max()]
            found_class_name = classname_with_highest_similarity.class_name.values[0]
            found_class_similarity = classname_with_highest_similarity.cosine_similarity.values[0]
            print(f"Class with highest similarity found: {found_class_name} with {found_class_similarity*100:.2f}% similarity\n")

            # verification based on the threshold
            found_class_object = project_class_components[found_class_name]

            # TODO: Ask the LLM for evaluation
            evaluation = LLMHelper.eval_suggestion(found_class_object.__str__(), llm, model, log_time)

            try:
                # extract the score using regex
                score_match = re.search(r"\d+", evaluation)
                # Extract the class type using the regex
                classification_match = re.search(r"(?i)(domain|implementation)", evaluation)
                
                eval_score = score_match.group()
                eval_classification = classification_match.group()
            except:
                print("Error extracting class type or score type.")
                eval_score = None
                eval_classification = None

            if found_class_similarity > config['general']['domain_threshold']:
                found_class_object.class_classification = ClassCategory.DOMAIN
                # add the class to the domain context
                domain_context += " and " + found_class_object.__str__()
                with open(f"artifacts/class_diagrams/{project_name}.puml", "a") as plantuml_file:
                    plantuml_file.write(f"{found_class_object.to_plantuml()}\n")
                print(f"Project {project_name} processed successfully...\n")
            else:
                found_class_object.class_classification = ClassCategory.IMPLEMENTATION

            classification_df = pd.concat([classification_df, pd.DataFrame({'class_name': [found_class_name], 'class_classification': [found_class_object.class_classification.value], 'class_similarity': [found_class_similarity], 'llm_evaluation': [evaluation]})])

            del project_class_components[found_class_name]
            df = df[df.class_name != found_class_name]
            i += 1
            log_df = pd.concat([log_df, pd.DataFrame({'list_of_given_concepts': [domain_context], 'concepts_suggested_by_llm': [suggested_concepts], 'closest_class': [found_class_name], 'cosine_similarity': [found_class_similarity], 'class_classification_similarity_based': [found_class_object.class_classification.value], 'llm_auto_classification': [eval_classification], 'll_auto_eval_score': [eval_score]})])
        # closing the plantuml file
        with open(f"artifacts/class_diagrams/{project_name}.puml", "a") as plantuml_file:
            plantuml_file.write(f"@enduml\n")
        # save the classification dataframe
        classification_df.to_csv(f"artifacts/data/{project_name}_classification.csv", index=False)
        # save the log dataframe
        log_df.to_csv(f"artifacts/data/{project_name}_summary.csv", index=False)
        print(f"Project {project_name} processed successfully...\n")



if __name__ == "__main__":
    main()