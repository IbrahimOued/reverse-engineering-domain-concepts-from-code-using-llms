import datetime
from config import project as config
import argparse
from utils.extract_signatures import create_signatures_dataframe
from utils.get_project_paths import get_folder_paths
from preprocessing.code_preprocessor import CodePreprocessor
from custom_models.custom_embedder import CustomEmbedder
import pandas as pd
from model.class_component import ClassCategory, ClassComponent, AttributeNode, MethodNode
from llm_helper import LLMHelper


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--path', dest='project_path', type=str, help='Specify the path of the project')
    # args = parser.parse_args()

    # project_path = args.project_path 
    # dictionary of all the projects

    repositories_folder = config['general']['repositories_folder']

    # walk through the project and extract the project folder names and paths
    repositories_dict = get_folder_paths(repositories_folder)

    # test the similarity between repo name and all the classes within the repo

        
    preprocessor = CodePreprocessor()
    custom_embedder = CustomEmbedder(model=config['models']['embedder'])
    llm = config['models']['llm']
    model = config['models']['model']

    # This is for all the projects
    for project_name, project_path in repositories_dict.items():
        sig_dataframe = create_signatures_dataframe(project_path=project_path)

        # create an empty dataframe
        df = pd.DataFrame(columns=['class_name', 'class_context', 'class_similarity'])
        
        # create a list of element of type ClassComponent
        project_class_components : dict[str, ClassComponent] = {}

        for class_name in sig_dataframe.class_name.unique().tolist():
            classname_tokens = preprocessor.tokenize_class_name(class_name)
            current_class = ClassComponent(class_name=class_name, class_name_tokens=classname_tokens, class_attributes=[], class_methods=[])

            for attribute in sig_dataframe.class_attributes.where(sig_dataframe.class_name == class_name).dropna().to_list()[0]:
                attr_tokens = preprocessor.tokenize_attributes_name(attribute)
                current_class.class_attributes.append(AttributeNode(attribute, attr_tokens))

            # Methods preprocessing
            for method_name in sig_dataframe.method_name.where(sig_dataframe.class_name == class_name).dropna().to_list():
                method_tokens = preprocessor.tokenize_method_name(method_name)
                if len(method_tokens) > 0:
                    current_class.class_methods.append(MethodNode(method_name, method_tokens))

            # summary text with class name, class attributes and class methods
            df = pd.concat([df, pd.DataFrame({'class_name': [class_name], 'class_context': [current_class.__str__()]})])
            # print(f"Class {class_name} processed successfully...\n")
            project_class_components[class_name] = current_class
        
        # TODO Using only the most likely domain class at this point, will use the pairs later
        most_likely_domain_class, second_most_likely_domain_class = custom_embedder.get_two_most_similar_classes(project_name, project_class_components)
        print(f"Most likely domain class: {most_likely_domain_class}\n")
        most_likely_domain_components = project_class_components[most_likely_domain_class]
        # delete the entrypoint class from the dictionary and the dataframe
        del project_class_components[most_likely_domain_class]
        df = df[df.class_name != most_likely_domain_class]

        # we will have a lot of heuristics that will come into play
        i = 1
        domain_context = most_likely_domain_components.__str__()
        classification_df = pd.DataFrame(columns=['class_name', 'class_classification', 'class_similarity'])
        # log the prompt and response
        log_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        while len(project_class_components) > 0:
            print(f"Starting iteration {i}...")
            # Should follow a particular template to ease comparison
            class_candidate = LLMHelper.generate_similar_concepts(domain_context, llm, model, log_time)
            df['cosine_similarity'] = df['class_name'].apply(lambda class_name: custom_embedder.calculate_similarity(class_name, class_candidate))
            classname_with_highest_similarity = df[df.cosine_similarity == df.cosine_similarity.max()]
            found_class_name = classname_with_highest_similarity.class_name.values[0]
            found_class_similarity = classname_with_highest_similarity.cosine_similarity.values[0]
            print(f"Class with highest similarity found: {found_class_name} with {found_class_similarity*100:.2f}% similarity\n")

            # verification based on the threshold
            found_class_object = project_class_components[found_class_name]
            if found_class_similarity > config['general']['domain_threshold']:
                found_class_object.class_classification = ClassCategory.DOMAIN
                # add the class to the domain context
                domain_context += " and " + found_class_object.__str__()
                print(f"Class {found_class_name} added to the domain context...\n")
            else:
                found_class_object.class_classification = ClassCategory.IMPLEMENTATION

            classification_df = pd.concat([classification_df, pd.DataFrame({'class_name': [found_class_name], 'class_classification': [found_class_object.class_classification.value], 'class_similarity': [found_class_similarity]})])

            del project_class_components[found_class_name]
            df = df[df.class_name != found_class_name]
            i += 1

        # store the dataframe in a csv file
        classification_df.to_csv(f"artifacts/similarity_scores/{project_name}_similarity_score.csv", index=False)
        # plot the similarity graph

        print(f"Process completed successfully for project {project_name}...")


if __name__ == "__main__":
    main()