from json import JSONEncoder, JSONDecoder

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Set the URL for the GraphQL endpoint
url = "https://fhict.instructure.com/api/graphql"

# Retrieve the authorization token from the environment variables
auth_token = os.getenv('AUTH_TOKEN')

# Set the headers, including the authorization header
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {auth_token}"
}

# Initialize an empty list to store all responses
all_data = []

# List of student IDs
students = JSONDecoder().decode(os.getenv('STUDENT_IDS'))

# Read the existing data from data/dump.json if it exists
try:
    with open('data/dump.json', 'r') as file:
        existing_data = json.load(file)
except FileNotFoundError:
    existing_data = []

# Iterate over each student ID
for student_id in students:
    # Format the query with the current student ID
    query = query_template = """
query MyQuery {
  allCourses {
    _id
    submissionsConnection(studentIds: """+student_id+""") {
      nodes {
        submissionHistoriesConnection {
          nodes {
            attempt
            user {
              _id
              email
            }
            score
            feedbackForCurrentAttempt
            rubricAssessmentsConnection {
              nodes {
                score
              }
            }
          }
        }
        assignment {
          _id
          name
        }
      }
    }
  }
}
"""

    # Make the POST request with the query and headers
    response = requests.post(url, json={'query': query}, headers=headers)

    # Parse the response JSON
    data = response.json()

    print("Data collected for student ID:", student_id, "", students.index(student_id),"/", len(students))
    # Merge the response data with the existing data
    for course in data["data"]["allCourses"]:
        existing_course = next((c for c in existing_data if c["_id"] == course["_id"]), None)
        if existing_course:
            existing_course["submissionsConnection"]["nodes"].extend(course["submissionsConnection"]["nodes"])
        else:
            existing_data.append(course)

# Write the combined data back to data/dump.json
with open('data/dump.json', 'w') as file:
    json.dump(existing_data, file, indent=4)