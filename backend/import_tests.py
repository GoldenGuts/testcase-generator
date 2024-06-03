import requests
import json
import time
import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

# Constants
BASE_URL = "https://xray.cloud.getxray.app/api/v1"
JSON_FILE_PATH = "result.json"
CLIENT_ID = os.getenv('xray_client_id')
CLIENT_SECRET = os.getenv('xray_client_secret')
COMPONENT_NAME = 'General'
LABEL_NAME = 'GenAi_testcase'
AUTH_TOKEN_FILE = "auth_token.json"

class XrayImport:

    def format_test_cases(self, json_data, jira_issue_id, xray_test_sets):
        print("Formatting test cases...")
        template = {
            "testtype": "Manual",
            "fields": {
                "project": {"key": jira_issue_id.split("-")[0]},
                "priority": {
                    "id": "10001"
                }
            },
            "update": {
                "issuelinks": [
                    {
                        "add": {
                            "type": {"name": "Test"},
                            "outwardIssue": {"key": jira_issue_id}
                        }
                    }
                ]
            },
            "xray_test_sets": [xray_test_sets]
        }
        
        return [
            {**template, "fields": {**template["fields"], "summary": test_case["summary"], "description": test_case["description"] + "\n *Precondition:* " + test_case["precondition"]}, "steps": test_case["steps"]}
            for test_case in json_data
        ]

    # xray
        
    def authenticate(self, client_id, secret):
        print("Authenticating with Xray...")
        payload = {"client_id": client_id, "client_secret": secret}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BASE_URL}/authenticate", json=payload, headers=headers)

        if response.status_code == 200:
            auth_token = response.json()  # Assuming the token is in the 'auth_token' field
            if auth_token:
                print("Auth token generated and saved.")
                return {"status": 200, "data": auth_token}
            else:
                print("Authentication succeeded but no token was returned.")
                return {"status": 200, "error": "Authentication succeeded but no token was returned."}
        else:
            print("Authentication failed with status:", response.status_code)
            return {"status": response.status_code, "error": "Authentication failed."}


    def post_test_cases(self, auth_token, test_cases):
        print("Posting test cases to Xray...")
        print(test_cases)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        response = requests.post(BASE_URL + "/import/test/bulk", json=test_cases, headers=headers)
        response.raise_for_status()
        
        print("Test cases posted successfully.")
        return response.json()["jobId"]

    def get_job_keys(self, auth_token, job_id):
        print("Polling for job completion...")
        headers = {"Authorization": f"Bearer {auth_token}"}
        while True:
            response = requests.get(BASE_URL + f"/import/test/bulk/{job_id}/status", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'successful':
                    print("Job completed successfully.")
                    return [issue['key'] for issue in data['result']['issues']]
            time.sleep(5)