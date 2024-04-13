import os
from jira import JIRA

class AddFields:
    def __init__(self, jira_email, jira_token):
        self.server = os.getenv('jira_endpoint')
        self.email = jira_email
        self.token = jira_token

    def add_fields(self, issue_key, component, labels):

        print(f"Updating JIRA issue {issue_key} with component '{component}' and label '{labels}'...")
        jiraOptions = {'server': self.server}
        user_email = self.email
        jira_token = self.token
        jira = JIRA(options=jiraOptions, basic_auth=(user_email, jira_token))

        new_components = [{'name': component}]

        issue = jira.issue(issue_key)

        issue.update(fields={'components': new_components})

        current_labels = issue.fields.labels
        for label in labels:
            if label not in current_labels:
                current_labels.append(label)
                issue.update(fields={"labels": [label]})

        print(f"JIRA issue {issue_key} setting to In Progress...")
        jira.transition_issue(issue_key, 51)
        print(f"JIRA issue {issue_key} updated.")

        return 