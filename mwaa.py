import boto3
import json

def update_mwaa_env_variables(env_name, updated_vars):
    client = boto3.client('mwaa')
    
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
    env_name = 'your_mwaa_environment_name'
    updated_vars = {
        'NEW_VAR_KEY': 'new_value'
    }
    update_mwaa_env_variables(env_name, updated_vars)
