import os
from jira import JIRA

import os
from dotenv import load_dotenv
load_dotenv()

from openai_service import OpenAIService

prompt_for_test_cases = '''
    The objective is to cover the following acceptance criteria: {{ac}} and validate the functionality of {{summary}} with {{description}}.
    Refer to the workflow : {{workflow}} to add more details or preconditions to the test case if necessary. {{user_prompt}}
    Please write the test cases (the number of test cases should be atleast 3).
    only provide data if required, otherwise omit the data key.
    just give as mentioned below without any formational changes.
    [
            {
                "summary": "This will be test name for test case 1",
                "description": "This will be test description for test case 1",
                "precondition": "This will be test preconditions for test case 1",
                "steps": [
                    {
                        "action": "some action related to test case 1 for step 1",
                        "data": "data related to test case 1 for step 1",
                        "result": "expected result 1."
                    },
                    {
                        "action": "some action related to test case 1 for step 2",
                        "data": "data related to test case 1 for step 2",
                        "result": "expected result 2"
                    },
                    {
                        "action": "some action related to test case 1 for step 3",
                        "data": "data related to test case 1 for step 3",
                        "result": "expected result 3"
                    }
                ]
            },
            {
                "summary": "This will be test name for test case 2",
                "description": "This will be test description for test case 2",
                "precondition": "This will be test preconditions for test case 2",
                "steps": [
                    {
                        "action": "some action related to test case 2 for step 1",
                        "data": "data related to test case 2 for step 1",
                        "result": "expected result 1."
                    },
                    {
                        "action": "some action related to test case 2 for step 2",
                        "data": "data related to test case 2 for step 3",
                        "result": "expected result 2"
                    },
                    {
                        "action": "some action related to test case 2 for step 3",
                        "data": "data related to test case 2 for step 3",
                        "result": "expected result 3"
                    }
                ]
            }
    ]
'''

prompt_for_workflow= "Generate Test strategy where functionality of {{summary}} with Description: {{description}} and Acceptance Criteria: {{ac}}. Please give scenarios titles only"
            
class JiraService :

    def __init__(self, jira_email, jira_token):
        self.server = os.getenv('JIRA_ENDPOINT')
        self.email = jira_email
        self.token = jira_token
        self.openai_api_key = os.getenv('API_KEY')
        
    def jira_auth(self):
        jiraOptions = {'server': self.server}
        jira = JIRA(options=jiraOptions, basic_auth=(self.email, self.token))
        user = jira.myself()
        return user['displayName']

    def start_generating(self, user_story_list, system_prompt, user_prompt, select_prompt="testcases"):
        jiraOptions = {'server': self.server}
        user_email = self.email
        jira_token = self.token
        jira = JIRA(options=jiraOptions, basic_auth=(user_email, jira_token))

        for x, i in enumerate(user_story_list):
            singleIssue = jira.issue(i)
            print(f"issue id {singleIssue.key}")
            story_data = {
                'id': singleIssue.id,
                'key': singleIssue.key,
                'summary': singleIssue.fields.summary,
                'description': singleIssue.fields.description,
                'workflow': singleIssue.fields.customfield_10059,
                'ac': singleIssue.fields.customfield_10060
            }

            if(select_prompt == "testcases"):
                print(f"{x+1} Generating test cases for story..{i}")
                base_prompt = prompt_for_test_cases
            if(select_prompt == "workflow"):
                print(f"{x+1} Generating workflow for story..{i}")
                base_prompt = prompt_for_workflow

            for key in ['summary', 'description', 'workflow', 'ac']:
                if story_data.get(key) is None:
                    continue
                base_prompt = base_prompt.replace('{{' + key + '}}', story_data[key])
                
            base_prompt = base_prompt.replace('{{user_prompt}}', user_prompt)
            
            print(f"System Prompt: {system_prompt}\nUser Prompt: {user_prompt}")

            result = OpenAIService(self.openai_api_key).get_completion(system_prompt, base_prompt)

            return result
