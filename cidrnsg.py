from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.network import NetworkManagementClient

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CIDRS_TO_DELETE = ["100.78.64.0/19"]

def delete_cidr_from_nsg_rules():
    credential = AzureCliCredential()
    subscription_client = SubscriptionClient(credential)

    for sub in subscription_client.subscriptions.list():
        subscription_id = sub.subscription_id
        network_client = NetworkManagementClient(credential, subscription_id)

        for nsg in network_client.network_security_groups.list_all():
            rg_name = nsg.id.split("/")[4]
            nsg_name = nsg.name

            for rule in network_client.security_rules.list(rg_name, nsg_name):
                modified = False
                if rule.source_address_prefixes:
                    for cidr in CIDRS_TO_DELETE:
                        if cidr in rule.source_address_prefixes:
                            rule.source_address_prefixes.remove(cidr)
                            modified = True

                if modified:
                    try:
                        network_client.security_rules.begin_create_or_update(
                            rg_name, nsg_name, rule.name, rule
                        ).result()
                        print(f"Updated rule: {rule.name}")
                    except Exception as e:
                        print(f"Error updating rule {rule.name}: {e}")

if __name__ == "__main__":
    delete_cidr_from_nsg_rules()