import os
from jira import JIRA, JIRAError
import requests
from requests.auth import HTTPBasicAuth

class JiraHelper:
    def __init__(self, jira_email, jira_token):
        self.server = os.getenv('JIRA_ENDPOINT')
        self.email = jira_email
        self.token = jira_token

    def add_fields(self, issue_key, component, labels):
        print(f"Updating JIRA issue {issue_key}...")

        jiraOptions = {'server': self.server}
        jira = JIRA(options=jiraOptions, basic_auth=(self.email, self.token))

        try:
            issue = jira.issue(issue_key)

            if component:
                try:
                    new_components = [{'name': component}]
                    issue.update(fields={'components': new_components})
                    print(f"Component '{component}' updated successfully.")
                except JIRAError as e:
                    if 'components' in e.response.json().get('errors', {}):
                        print(f"Error updating component: {e.response.json()['errors']['components']}")
                        raise PermissionError(e.response.json()['errors']['components'])
                    else:
                        print(f"Error updating component: {e}")
                        raise

            if len(labels) > 0:
                try:
                    issue.update(fields={"labels": labels})
                    print(f"Labels '{labels}' updated successfully.")
                except JIRAError as e:
                    if 'labels' in e.response.json().get('errors', {}):
                        print(f"Error updating labels: {e.response.json()['errors']['labels']}")
                        raise PermissionError(e.response.json()['errors']['labels'])
                    else:
                        print(f"Error updating labels: {e}")
                        raise

            print(f"JIRA issue {issue_key} setting to In Progress...")
            jira.transition_issue(issue, 51)  # Assumes '51' is the ID for "In Progress"
            print(f"JIRA issue {issue_key} updated to In Progress.")

        except JIRAError as e:
            print(f"Failed to update JIRA issue {issue_key}: {e}")
            raise


    def get_labels(self):
        jira_url = self.server
        jira_user = self.email
        jira_token = self.token
        
        # Endpoint to get all labels
        url = f"{jira_url}/rest/api/3/label"

        labels = []
        start_at = 0
        total = None

        while total is None or start_at < total:
            # Make the request to the API
            response = requests.get(
                f"{url}?startAt={start_at}",
                auth=HTTPBasicAuth(jira_user, jira_token)
            )

            if response.status_code == 200:
                data = response.json()
                labels.extend(data['values'])
                total = data['total']  # Total number of labels across all pages
                start_at += len(data['values'])  # Update startAt for the next page
                print(f"Retrieved {len(data['values'])} labels, Total so far: {len(labels)}")
            else:
                print(f"Failed to retrieve labels. Status code: {response.status_code}, Response: {response.text}")
                break

        print(f"Total labels retrieved: {len(labels)}")
        return labels
    
    def set_workflow(self, issue_key, workflow):
        print(f"Updating JIRA issue {issue_key} with workflow")
        jiraOptions = {'server': self.server}
        user_email = self.email
        jira_token = self.token
        jira = JIRA(options=jiraOptions, basic_auth=(user_email, jira_token)) 
        try:
            issue = jira.issue(issue_key)
            old_workflow = issue.fields.customfield_10059
            issue.update(fields={'customfield_10059': old_workflow+'\n'+workflow})
            print(f"JIRA issue {issue_key} updated with workflow '{workflow}'")
        except JIRAError as e:
            print(f"Failed to update JIRA issue {issue_key}: {e}")
            raise
        
    def get_components(self, project_key):
        print(f"Getting components for project {project_key}")
        jiraOptions = {'server': self.server}
        user_email = self.email
        jira_token = self.token
        jira = JIRA(options=jiraOptions, basic_auth=(user_email, jira_token))
        components = jira.project_components(project_key)
        components_names = [component.name for component in components] 
        return components_names
