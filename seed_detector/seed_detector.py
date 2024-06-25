from sentence_transformers import util

def detect_project_seed(embedder, project_name, class_list):
    # initialize the get the number of vote for each class
    class_votes = {}
    detection_rules = ['using_class_name', 'using_packages', 'using_readme', 'using_vcs_metadata']

    for detection_rule in detection_rules:
        if detection_rule == 'using_class_name':
            highest_ranked_class = detect_using_class_name(embedder, project_name, class_list)
            if highest_ranked_class is not None:
                # update the vote with plus 1
                if class_votes.get(highest_ranked_class) is None:
                    class_votes[highest_ranked_class] = 1
                class_votes[highest_ranked_class] = class_votes.get(highest_ranked_class, 0) + 1
        elif detection_rule == 'using_packages':
            highest_ranked_class = detect_using_packages(embedder, project_name, class_list)
            if highest_ranked_class is not None:
                # update the vote with plus 1
                if class_votes.get(highest_ranked_class) is None:
                    class_votes[highest_ranked_class] = 1
                class_votes[highest_ranked_class] = class_votes.get(highest_ranked_class, 0) + 1
        elif detection_rule == 'using_readme':
            highest_ranked_class = detect_using_readme(embedder, project_name, class_list)
            if highest_ranked_class is not None:
                # update the vote with plus 1
                if class_votes.get(highest_ranked_class) is None:
                    class_votes[highest_ranked_class] = 1
                class_votes[highest_ranked_class] = class_votes.get(highest_ranked_class, 0) + 1
        elif detection_rule == 'using_vcs_metadata':
            highest_ranked_class = detect_using_vcs_metadata(embedder, project_name, class_list)
            if highest_ranked_class is not None:
                if class_votes.get(highest_ranked_class) is None:
                    class_votes[highest_ranked_class] = 1
                # update the vote with plus 1
                class_votes[highest_ranked_class] = class_votes.get(highest_ranked_class, 0) + 1

    # get the class with the highest number of votes
    most_likely_domain_class = max(class_votes, key=class_votes.get)
    # get the second most likely class
    del class_votes[most_likely_domain_class]
    if len(class_votes) == 0:
        return most_likely_domain_class, None
    second_most_likely_domain_class = max(class_votes, key=class_votes.get)
    return most_likely_domain_class, second_most_likely_domain_class



def detect_using_class_name(embedder, project_name, class_list):
    max_similarity = 0
    most_similar_class = None
    for class_name, _ in class_list.items():
        similarity = embedder.calculate_similarity(project_name, class_name)
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_class = class_name
    return most_similar_class

def detect_using_packages(embedder, project_name, class_list):
    pass

def detect_using_readme(embedder, project_name, class_list):
    pass

def detect_using_vcs_metadata(embedder, project_name, class_list):
    pass