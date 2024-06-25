import nltk
nltk.download('wordnet')
from nltk import PorterStemmer
from nltk.stem import WordNetLemmatizer
import stanza


class CodePreprocessor:
    porter_stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,mwt')

    @classmethod
    def stem_token(cls, token):
        return cls.porter_stemmer.stem(token)

    @classmethod
    def lemmatize_token(cls, token):
        return cls.lemmatizer.lemmatize(token)

    @classmethod
    def tokenize_class_name(cls, class_name):
        result = []
        if (class_name.isupper()):
            class_name = class_name.title()
        for char in class_name:
            if char.isupper() and result:
                result.append('_')
            result.append(char)
        # Perform lemmatization and stemming pipeline before returning
        raw_text = ''.join(result).lower().split('_')
        # TODO: Create a function for this
        merged_list = cls.merge_singletons(raw_text)
        filtered_tokens = cls.filter_valid_tokens(merged_list)
        lemmatized_tokens = [cls.lemmatize_token(
            token) for token in filtered_tokens]
        return lemmatized_tokens

    @classmethod
    def tokenize_attributes_name(cls, attribute):
        if attribute:
            result = []
            if (attribute.isupper()):
                attribute = attribute.title()
            for char in attribute:
                if char.isupper() and result:
                    result.append('_')
                result.append(char)
            raw_text = ''.join(result).lower().split('_')
            merged_list = cls.merge_singletons(raw_text)
            filtered_tokens = cls.filter_valid_tokens(merged_list)
            lemmatized_tokens = [cls.lemmatize_token(
                token) for token in filtered_tokens]
            return lemmatized_tokens

    @classmethod
    def tokenize_method_name(cls, method_signature):
        result = []
        method_name, parameters = method_signature.split('(')
        # parameters = parameters[:-1] TODO: I removed the parameters because they don't add much information to the whole thing
        # method name
        if (method_name.isupper()):
            method_name = method_name.title()

        for char in method_name:
            if char.isupper() and result:
                result.append('_')
            result.append(char)

        raw_text = ''.join(result).lower().split('_')
        merged_list = cls.merge_singletons(raw_text)
        filtered_tokens = cls.filter_valid_tokens(merged_list)
        lemmatized_tokens = [cls.lemmatize_token(
            token) for token in filtered_tokens]
        return lemmatized_tokens

    @classmethod
    def filter_valid_tokens(cls, merged_list):
        sanitized_tokens = []
        for token in merged_list:
            if token != ' ' and token != '':
                doc = cls.nlp(token)
                sentence = doc.sentences[0]  # Assuming single sentence
                for token in sentence.words:
                    if token.upos != 'X':
                        sanitized_tokens.append(token.text)
        return sanitized_tokens

    def merge_singletons(word_list):
        merged_list = []
        current_word = ''

        for word in word_list:
            if len(word) == 1:
                current_word += word
            else:
                if current_word:
                    merged_list.append(current_word)
                    current_word = ''
                merged_list.append(word)

        if current_word:
            merged_list.append(current_word)

        return merged_list