import json
import subprocess

# Path to your JSON file containing the variables
json_file = 'variables.json'
# URL of your Airflow webserver
airflow_url = 'https://<your-airflow-webserver-url>/api/v1/variables'
# Your session cookie value
session_cookie = '<your_session_cookie_value>'

# Load the variables from the JSON file
with open(json_file, 'r') as file:
    variables = json.load(file)

# Loop through each variable and update/create it via a curl command
for var in variables:
    curl_cmd = [
        'curl', '-X', 'POST', airflow_url,
        '-H', 'Content-Type: application/json',
        '-H', 'Accept: application/json',
        '-H', f'Cookie: session={session_cookie}',
        '-d', json.dumps({
            "key": var['key'],
            "value": var['value'],
            "description": var['description']
        })
    ]
    # Execute the curl command
    process = subprocess.run(curl_cmd, capture_output=True, text=True)
    print(f"Processed variable: {var['key']}, Status: {process.returncode}, Response: {process.stdout}")
