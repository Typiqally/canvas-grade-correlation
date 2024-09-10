# Format GraphQl response to a more readable format to calculate with
import json
import uuid
collection = {}

for course in json.load(open('data/dump.json')):
    for sub in course['submissionsConnection']['nodes']:
        assignmentId = sub['assignment']['_id']
        attempts = sub['submissionHistoriesConnection']['nodes']

        for attempt in attempts:
            rubric_nodes = attempt["rubricAssessmentsConnection"]["nodes"]
            user_id = attempt['user']['_id']

            if user_id not in collection:
                collection[user_id] = {}
            if assignmentId not in collection[user_id]:
                collection[user_id][assignmentId] = []

            if rubric_nodes:
                collection[user_id][assignmentId].append(rubric_nodes[0]['score'])
            elif attempt['feedbackForCurrentAttempt']:
                if collection[user_id][assignmentId]: # if there are previous scores
                    collection[user_id][assignmentId].append(collection[user_id][assignmentId][-1])

filtered_list = {
    user: {
        assignment: scores
        for assignment, scores in assignments.items() if len(scores) >= 2
    }
    for user, assignments in collection.items() if len(assignments) > 0
}


def replace_none_with_zero(scores):
    return [0 if score is None else score for score in scores]

def remove_starting_zeros(arr):
    # Find the index of the first non-zero element
    first_non_zero_index = next((i for i, x in enumerate(arr) if x != 0), len(arr))
    # Return the sub-array starting from the first non-zero element
    return arr[first_non_zero_index:]


# Update filtered_list with zero for None
for user, assignments in filtered_list.items():
    for assignment, scores in assignments.items():
        scores = replace_none_with_zero(scores)
        scores = remove_starting_zeros(scores)
        filtered_list[user][assignment] = scores


# Function to calculate delta change percentage
def calculate_delta_change_percentage(scores):
    return [(scores[i] - scores[i - 1]) / scores[i - 1] * 100 if scores[i - 1] != 0 else 0 for i in
            range(1, len(scores))]

def anonymize_filtered_list(filtered_list):
    user_mapping = {}
    assignment_mapping = {}

    anonymized_list = {}

    for user_id, assignments in filtered_list.items():
        if user_id not in user_mapping:
            user_mapping[user_id] = str(uuid.uuid4())
        anonymized_user_id = user_mapping[user_id]

        anonymized_list[anonymized_user_id] = {}

        for assignment_id, data in assignments.items():
            if assignment_id not in assignment_mapping:
                assignment_mapping[assignment_id] = str(uuid.uuid4())
            anonymized_assignment_id = assignment_mapping[assignment_id]

            anonymized_list[anonymized_user_id][anonymized_assignment_id] = data

    return anonymized_list

# Example usage



# Update filtered_list with zero for None and calculate delta changes percentage
for user, assignments in filtered_list.items():
    for assignment, scores in assignments.items():
        scores = replace_none_with_zero(scores)
        delta_changes = calculate_delta_change_percentage(scores)
        filtered_list[user][assignment] = {
            'scores': scores,
            'delta_changes_percentage': delta_changes
        }

# Filter out users who do not have assignments/scores
filtered_list = {
    user: assignments
    for user, assignments in filtered_list.items()
    if any(scores['scores'] for scores in assignments.values())
}

anonymized_filtered_list = anonymize_filtered_list(filtered_list)



with open('dataset.json', 'w') as file:
    json.dump(anonymized_filtered_list , file)