import boto3
import json

def get_customer_managed_kms_policies():
    # Create a KMS client
    client = boto3.client('kms')

    # Initialize a paginator for the list_keys operation
    paginator = client.get_paginator('list_keys')

    # Collect all customer-managed KMS keys
    for page in paginator.paginate():
        for key in page['Keys']:
            # Get metadata to check if the key is customer-managed
            metadata = client.describe_key(KeyId=key['KeyId'])['KeyMetadata']
            if metadata['KeyManager'] == 'CUSTOMER':
                key_id = metadata['KeyId']
                # Fetch the policies for each customer-managed key
                policies = client.list_key_policies(KeyId=key_id)['PolicyNames']
                for policy_name in policies:
                    # Retrieve the actual policy document
                    policy = client.get_key_policy(KeyId=key_id, PolicyName=policy_name)['Policy']
                    policy_data = json.loads(policy)
                    
                    # Define a filename using both the key ID and the policy name
                    filename = f'{key_id}_{policy_name}.json'
                    # Write the policy to a separate file
                    with open(filename, 'w') as file:
                        json.dump(policy_data, file, indent=4)
                    print(f"Policy {policy_name} for key {key_id} written to '{filename}'")

def main():
    get_customer_managed_kms_policies()

if __name__ == "__main__":
    main()