import os
import requests
from jira import JIRA
import re, json
from dotenv import load_dotenv
load_dotenv()

from openai_service import OpenAIService

system_prompt_for_test_cases = '''
You are an assistant to an application that generates test cases for quality engineers (QEs) at a software company who are testing features and products currently under development. I will pass you the the name,description, workflow, and acceptance criteria (AC) specified for a development item. Using this information, please generate a json array of clear, reasonably detailed, and comprehensive test cases that will allowthe QEs to confirm that the defined functionality either works or does not work as intended. Each test case should clearly specify the set of actions that a QE should take to execute the test case. Generate enoughtest cases to confirm each aspect of the defined workflow. 
The array of test cases must adhere to the following json scheme:
[{"summary":"name of test case","description":"description of test case","precondition":"preconditions that must exist for executing the test case","steps":[{"action":"literal action to execute","data":"data needed to execute action","result":"expected result of executing this action"}]}]
'''

user_prompt_for_test_cases = "Given the information for the following development item, generate maximum set of test cases (in JSON Array provided) for {{summary}} with Description: {{description}}, Workflow: {{workflow}} and Acceptance Criteria: {{ac}} {{additional_user_input}}."

prompt_for_workflow= "Generate Test strategy where functionality of {{summary}} with Description: {{description}} and Acceptance Criteria: {{ac}} {{additional_user_input}}. Please give scenarios titles only"
    

def clean_text(text):
    """
    This function removes asterisks, extra spaces, hyperlinks, text inside '{' and '}' brackets,
    and text enclosed inside "!" symbols from a string.

    Args:
        text: The string to be cleaned.

    Returns:
        The cleaned string.
    """
    pattern = r"\*|\s{2,}|\n|https?://\S+|\!\S+\!|\{\S+\}|\[\S+\]"
    cleaned_text = re.sub(pattern, "", text)
    return cleaned_text + ". "

def get_search_query(title, description, acceptance_criteria):
    """
    This function constructs a search query by combining the provided title, description, and acceptance criteria.

    Args:
        title: The title of the item to be searched for (string).
        description: The description of the item to be searched for (string).
        acceptance_criteria: The acceptance criteria for the item to be searched for (string).

    Returns:
        A combined search query string formed by cleaning and concatenating the provided arguments (string).

    Notes:
        - The function attempts to clean and combine the arguments using the `clean_text` function.
        - In case of any exceptions during the cleaning process, the original (uncleaned) arguments are used to construct the search query.
    """
    search_query = ""
    try:
        if title:
            search_query += clean_text(title)

        if description:
            search_query += clean_text(description)

        if acceptance_criteria:
            search_query += clean_text(acceptance_criteria)

        return search_query
    except:
        return search_query

def get_documentation(drsAccessToken, searchQuery, top_p=10, min_relevance_score=0.6):
    """
    This function retrieves relevant documentation from a remote API using a provided access token and search query.

    Args:
        drsAccessToken: A valid access token for the documentation retrieval service (string).
        searchQuery: The search query to use for retrieving documentation (string).
        top_p (optional): The maximum number of documentation items to return (integer). Defaults to 10.
        min_relevance_score (optional): The minimum relevance score required for inclusion (float). Defaults to 0.6.

    Returns:
        A list of strings containing the retrieved documentation snippets, or an empty list if retrieval fails.

    Raises:
        - Any exceptions raised during the API request or data processing (specific exceptions not listed).

    Notes:
        - This function uses the `requests` library to make an HTTP GET request to a remote API.
        - The API endpoint URL and expected data format are assumed to be known and not configurable through this function.

    """
    relevant_documentation = ""
    try:

        url = "https://gait-rag-services-poc.azurewebsites.net/api/v1/documentation"

        params = {
            "search_query": searchQuery,
            "max_items": top_p,
            "min_relevance_score": min_relevance_score,
        }

        headers = {"Authorization": drsAccessToken}

        response = requests.request("GET", url, headers=headers, params=params).json()
        response = response.get("response")

        relevant_documentation = [element["chunk"] for element in response]

        return relevant_documentation

    except:
        return relevant_documentation

class JiraService:
    def __init__(self, jira_email, jira_token):
        self.server = os.getenv("JIRA_ENDPOINT")
        self.email = jira_email
        self.token = jira_token
        self.openai_api_key = os.getenv("API_KEY")

    def jira_auth(self):
        jiraOptions = {"server": self.server}
        jira = JIRA(options=jiraOptions, basic_auth=(self.email, self.token))
        user = jira.myself()
        return user["displayName"]

    def start_generating(
        self, user_story_list, additional_user_input, select_prompt="testcases",
        drsAccessToken=None
    ):
        jiraOptions = {"server": self.server}
        user_email = self.email
        jira_token = self.token
        jira = JIRA(options=jiraOptions, basic_auth=(user_email, jira_token))

        for x, i in enumerate(user_story_list):
            singleIssue = jira.issue(i)
            print(f"issue id {singleIssue.key}")

            if select_prompt == "testcases":
                # setting system prompt for testcases
                # base prompt is user prompt with additional details + any other user input
                system_prompt = system_prompt_for_test_cases

                searchQuery = get_search_query(
                    singleIssue.fields.summary,
                    singleIssue.fields.description,
                    singleIssue.fields.customfield_10060,
                )

                print(
                    f"Gathering relevant documentation from Azure AI Search for story."
                )
                relevant_documentation = get_documentation(drsAccessToken, searchQuery)

                print(f"{x+1} Generating test cases for story..{i}")

                if relevant_documentation:
                    base_prompt = """
                        Here's a summary of relevant content retrieved from Azure AI Search for your query:
                        {}
                        **User Query:** {}
                    """.format(
                        relevant_documentation, user_prompt_for_test_cases
                    )
                else:
                    base_prompt = user_prompt_for_test_cases

            if select_prompt == "workflow":
                print(f"{x+1} Generating workflow for story..{i}")
                base_prompt = prompt_for_workflow

            story_data = {
                "id": singleIssue.id,
                "key": singleIssue.key,
                "summary": singleIssue.fields.summary,
                "description": singleIssue.fields.description,
                "workflow": singleIssue.fields.customfield_10059,
                "ac": singleIssue.fields.customfield_10060,
            }
            for key in ["summary", "description", "workflow", "ac"]:
                if story_data.get(key) is None:
                    continue
                base_prompt = base_prompt.replace("{{" + key + "}}", story_data[key])

            base_prompt = base_prompt.replace("{{additional_user_input}}", additional_user_input)

            print(f"System Prompt: {system_prompt}\nUser Prompt: {base_prompt}")

            result = OpenAIService(self.openai_api_key).get_completion(
                system_prompt, base_prompt
            )

            return result
