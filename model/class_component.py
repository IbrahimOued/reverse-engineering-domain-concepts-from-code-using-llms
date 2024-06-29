from enum import Enum

class MethodNode:
    method_name: str
    method_name_tokens: list[str]

    def __init__(self, method_name, method_name_tokens):
        self.method_name = method_name
        self.method_name_tokens = method_name_tokens

    def __str__(self):
        return f"[{', '.join(self.method_name_tokens)}]"

    def get_methods_tokenized(self):
        return ', '.join(self.class_methods)


class AttributeNode:
    attribute_name: str
    attribute_name_tokens: list[str]

    def __init__(self, attribute_name, attribute_name_tokens):
        self.attribute_name = attribute_name
        self.attribute_name_tokens = attribute_name_tokens

    def __str__(self):
        return f"{self.attribute_name}"

    def get_attributes_tokenized(self):
        return ', '.join(self.attribute_name_tokens)

class ClassCategory(Enum):
    DOMAIN = "domain"
    IMPLEMENTATION = "implementation"

# TODO: Replace by behaviors 

class ClassComponent:
    class_name: str
    class_classification: ClassCategory
    class_name_tokens: list[str]
    class_attributes: list[AttributeNode]
    class_methods: list[MethodNode]

    def __init__(self, class_name, class_name_tokens, class_attributes, class_methods):
        self.class_name = class_name
        self.class_name_tokens = class_name_tokens
        self.class_attributes = class_attributes
        self.class_methods: MethodNode = class_methods

    def __str__(self):
        class_sentence = f"{self.class_name} [{self.get_classname_tokens()}] "
        attributes_sentences = []
        methods_sentences = []
        if len(self.class_attributes) > 0:
            for attribute in self.class_attributes:
                attributes_sentences.append(f"{attribute}")
        if len(self.class_methods) > 0:
            for method in self.class_methods:
                methods_sentences.append(f"{method}")
        if len(attributes_sentences) == 0 and len(methods_sentences) == 0:
            class_sentence += "no properities nor behaviors"
        elif len(attributes_sentences) == 0 and len(methods_sentences) > 0:
            class_sentence += f"no properties and characterized by these behaviors: {', '.join(methods_sentences)}"
        else:
            class_sentence += f"represented by these properties: {', '.join(attributes_sentences)} and characterized by these behaviors: {', '.join(methods_sentences)}"

        return class_sentence
        # return ', '.join(self.class_name_tokens)

    def get_classname_tokens(self):
        # return "[" + ', '.join(self.class_name_tokens) + "]"
        return ', '.join(self.class_name_tokens)

    def to_plantuml(self):
        uml = f"class {self.class_name} {{\n"
        
        if self.class_attributes:
            for attribute in self.class_attributes:
                uml += f"  {attribute.attribute_name}\n"
        
        if self.class_methods:
            for method in self.class_methods:
                uml += f"  {method.method_name}()\n"
        
        uml += "}"
        
        return uml