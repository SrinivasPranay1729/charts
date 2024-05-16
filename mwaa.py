import boto3
import json

def update_mwaa_env_variables(env_name, updated_vars, region):
    client = boto3.client('mwaa', region_name=region)
    
    # Get the current configuration
    response = client.get_environment(Name=env_name)
    current_vars = response['Environment']['EnvironmentVariables']
    
    # Update the variables
    current_vars.update(updated_vars)
    
    # Update the environment
    client.update_environment(
        Name=env_name,
        EnvironmentVariables=current_vars
    )

if __name__ == "__main__":
    env_name = 'your_mwaa_environment_name'  # Replace with your environment name
    updated_vars = {
        'NEW_VAR_KEY': 'new_value'  # Replace or add new key-value pairs as needed
    }
    region = 'your_aws_region'  # Specify the AWS region here, e.g., 'us-east-1'
    update_mwaa_env_variables(env_name, updated_vars, region)
