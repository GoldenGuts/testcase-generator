from flask import Flask, request, jsonify, make_response
from helper import extract_and_repair_json
from get_test_cases import JiraService
from import_tests import XrayImport
from jira_helper import JiraHelper
import jwt, json, os
import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask_cors import CORS

import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)
# app.config['DEBUG'] = True

SECRET_KEY = os.getenv('SECRET_KEY')

# Temporary in-memory storage
vectorization_keys = {}

# Setup logging
if not app.debug:
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test", methods=['POST'])
def test():
    try:
        # Assuming JSON input...
        data = request.get_json()
        # Your logic here...
        return jsonify(data), 200
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/post_example', methods=['POST'])
def post_example():
    # Retrieve data from the POST request
    data = request.json  # Assuming the request data is in JSON format
    
    # Process the data (e.g., perform some computation or database operation)
    processed_data = data['key']  # Assuming the JSON data has a key named 'key'
    
    # Return a response (e.g., send a JSON response)
    response = {'message': 'Received and processed data successfully', 'processed_data': processed_data}
    return jsonify(response), 200  # Return a JSON response with a 200 status code


@app.route("/get_test_cases", methods=["POST"])
def get_test_cases():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1]  # Extract the token part of the header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    jira_email = payload["email"]
    jira_token = payload["token"]

    data = request.get_json()
    jira_issue_id = data.get("issue_id")
    system_prompt = data.get("system_prompt", "")
    user_prompt = data.get("user_prompt", "As a quality engineer, I need to create XRay test cases for a desktop application named Litera Secure Share.")
    
    try:
        response = JiraService(jira_email, jira_token).start_generating(jira_issue_id, system_prompt, user_prompt)
        repaired_json = extract_and_repair_json(response)
        return jsonify(repaired_json), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate test cases, details in console!", "details": str(e)}), 500


@app.route("/get_workflow", methods=["POST"])
def get_workflow():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1]  # Extract the token part of the header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    jira_email = payload["email"]
    jira_token = payload["token"]

    data = request.get_json()
    
    jira_issue_id = data.get("issue_id")
    system_prompt = data.get("system_prompt", "")
    user_prompt = data.get("user_prompt", "As a quality engineer, ")
    
    response = JiraService(jira_email, jira_token).start_generating(jira_issue_id, system_prompt, user_prompt, select_prompt="workflow")
    return jsonify(response), 200

@app.route("/post_test_cases", methods=["POST"])
def post_test_cases():
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1] 

    data = request.get_json()

    testcase_json = json.loads(data.get('testcase_data'))
    xray_set = data.get('xray_test_sets')
    jira_issue_id = data.get('jira_issue_id')

    try:
        formatted_data = XrayImport().format_test_cases(testcase_json, jira_issue_id, xray_set)
        job_id = XrayImport().post_test_cases(token, formatted_data)
        keys = XrayImport().get_job_keys(token, job_id)
        return jsonify(keys), 200
    except Exception as e:
        return make_response(jsonify({"error": "XRay Authentication Failed!"}), 401)

@app.route("/update_jira_workflow", methods=["POST"])
def update_jira_workflow():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    jira_email = payload["email"]
    jira_token = payload["token"] 
    
    try:
        data = request.json
        jira_issue_id = data.get('jira_issue_id')
        workflow = data.get('workflow')
        JiraHelper(jira_email, jira_token).set_workflow(jira_issue_id, workflow)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Failed to update issue", "details": str(e)}), 500
    
    response = {'message': 'Workflow Updated Successfully'}
    return jsonify(response), 200

@app.route("/add_fields", methods=["POST"])
def add_fields():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1]  # Extract the token part of the header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    jira_email = payload["email"]
    jira_token = payload["token"]
    
    data = request.json
    key = request.args.get('key')
    labels = data.get("labels", [])
    component = data.get("component", None)
    
    print(f"Adding fields to JIRA issue {key}...")
    print(f"Label: {labels}")
    print(f"Component: {component}")
    
    try:
        JiraHelper(jira_email, jira_token).add_fields(key, component, labels)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to update issue", "details": str(e)}), 500

    response = {'message': 'Issue Updated Successfully'}
    return jsonify(response), 200


@app.route("/authenticate", methods=["POST"])
def authenticateJira():
    
    data = request.json

    jira_email = data["jira_email"]
    jira_token = data["jira_token"]
    
    try:
        displayName = JiraService(jira_email, jira_token).jira_auth()
        print(displayName)
    except Exception as e:
        return make_response(jsonify({"error": "Internal Server Error", "message": str(e)}), 500)
    
    def create_jwt(user_data):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        token = jwt.encode(user_data, SECRET_KEY, algorithm='HS256')
        return token

    user_credentials = {
        'email': jira_email,
        'token': jira_token,
    }

    my_jwt = create_jwt(user_credentials)
    response = {'message': 'Successfully created JWT', 'jwt': my_jwt, 'user': displayName}
    return jsonify(response), 200

@app.route("/get-jira-labels", methods=["GET"])
def get_jira_labels():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    jira_email = payload["email"]
    jira_token = payload["token"]

    try:
        labels = JiraHelper(jira_email, jira_token).get_labels()
        response = {'message': 'Successfully retrieved labels', 'labels': labels}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving Jira labels"}), 500

@app.route("/get-jira-components", methods=["GET"])
def get_jira_components():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    jira_email = payload["email"]
    jira_token = payload["token"]
    project_id = request.args.get('project_id')

    try:
        components = JiraHelper(jira_email, jira_token).get_components(project_id)
        response = {'message': 'Successfully retrieved components', 'components': components}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving Jira components", "details": str(e)}), 500

@app.route("/authenticate-xray", methods=["POST"])
def authenticate_xray():
    data = request.json
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    if not client_id or not client_secret:
        print("Client ID or client secret not provided.")
        return make_response(jsonify({"error": "Client ID or Client Secret not provided"}), 400)

    try:
        print("Attempting to authenticate.")
        auth_response = XrayImport().authenticate(client_id, client_secret)
        
        print(f"Authentication status: {auth_response['status']}")

        if auth_response.get('status') == 200:
            print("Authentication successful.")
            return jsonify({"message": "Authentication successful", "token": auth_response['data']}), 200
        elif auth_response.get('status') == 401:
            return make_response(jsonify({"error": "Authentication failed"}), 401)
        else:
            print(f"Unexpected status: {auth_response.get('status')}")
            return make_response(jsonify({"error": "Unexpected status received", "status": auth_response.get('status')}), auth_response.get('status'))

    except Exception as e:
        print(f"An exception occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error", "message": str(e)}), 500)

@app.route('/store-vectorization-key', methods=['POST'])
def store_vectorization_key():
    data = request.json
    vectorization_api_key = data.get('vectorization_api_key')
    
    if not vectorization_api_key:
        return jsonify({"error": "No vectorization API key provided"}), 400

    # Store the vectorization key in the in-memory dictionary
    vectorization_keys['key'] = vectorization_api_key

    return jsonify({"message": "Vectorization API key stored successfully"}), 200

@app.route('/get-vectorization-key', methods=['GET'])
def get_vectorization_key():
    vectorization_api_key = vectorization_keys.get('key')
    
    if vectorization_api_key:
        return jsonify({"vectorization_api_key": vectorization_api_key}), 200
    else:
        return jsonify({"error": "No vectorization API key found"}), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5006, debug=True, use_reloader=False)