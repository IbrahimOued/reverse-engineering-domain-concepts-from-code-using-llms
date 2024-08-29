import os
import pandas as pd
import javalang

def find_java_classes(folder_path):
    java_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files

def extract_signatures(java_file):
    with open(java_file, "r", encoding="utf-8") as file:
        code = file.read()

    tree = javalang.parse.parse(code)

    class_name = None
    methods = []
    class_attributes = []
    # method_attributes = {}

    for path, node in tree:
        if isinstance(node, javalang.tree.Import):
            # You can process import statements if needed
            pass
        elif isinstance(node, javalang.tree.ClassDeclaration):
            class_name = node.name
            # Extracting class attributes
            for field in node.fields:
                # attribute = field.type.name + " " + field.declarators[0].name
                attribute = field.declarators[0].name
                class_attributes.append(attribute)
            # only methods defined directly in the class
            for method in node.methods:
                method_signature = method.name + "(" + ", ".join(param.type.name for param in method.parameters) + ")"
                methods.append(method_signature)

    return class_name, class_attributes, methods # , method_attributes


def create_signatures_dataframe(project_path):
    data = {'class_name': [], 'method_name': [], 'class_attributes': []} # , 'method_attributes': []}
    java_files = find_java_classes(project_path)
    for java_file in java_files:
        class_name, class_attributes, methods = extract_signatures(java_file)
        for method in methods:
            data['class_attributes'].append(class_attributes)
            data['class_name'].append(class_name)
            data['method_name'].append(method)
            # data['method_attributes'].append(methods_attributes[method.split('(')[0]])
    df = pd.DataFrame(data)
    return df
