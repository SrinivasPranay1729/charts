import boto3
import json

def get_customer_managed_kms_policies():
    # Create a KMS client
    client = boto3.client('kms')

    # Initialize a paginator for the list_keys operation
    paginator = client.get_paginator('list_keys')
    customer_keys = []

    # Collect all customer-managed KMS keys
    for page in paginator.paginate():
        for key in page['Keys']:
            # Get metadata to check if the key is customer-managed
            metadata = client.describe_key(KeyId=key['KeyId'])['KeyMetadata']
            if metadata['KeyManager'] == 'CUSTOMER':
                customer_keys.append(metadata['KeyId'])

    # Dictionary to hold key IDs and their policies
    policies = {}

    # Fetch the policies of customer-managed keys
    for key_id in customer_keys:
        # List policies associated with the key
        policy_names = client.list_key_policies(KeyId=key_id)['PolicyNames']
        key_policies = []
        for policy_name in policy_names:
            policy = client.get_key_policy(KeyId=key_id, PolicyName=policy_name)['Policy']
            # Convert JSON string to a dictionary and append to the list
            key_policies.append(json.loads(policy))
        policies[key_id] = key_policies

    # Write the collected policies to a file
    with open('customer_managed_kms_policies.json', 'w') as f:
        json.dump(policies, f, indent=4)

    print(f"Saved policies of {len(customer_keys)} customer-managed keys to 'customer_managed_kms_policies.json'")

def main():
    get_customer_managed_kms_policies()

if __name__ == "__main__":
    main()