# reclaim_cidr_nsg.py
# pip install azure-identity azure-mgmt-resource azure-mgmt-network

"""
Reclaim specified CIDR prefixes from Azure Network Security Group (NSG) rules.

This script:
- Authenticates using Azure CLI credentials.
- Iterates over all Azure subscriptions accessible to the logged-in account.
- Lists NSG rules and removes any source_address_prefixes matching the CIDRs to delete.
- Updates the modified rules and logs results to console and file.

Author: Sriram
"""

from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.network import NetworkManagementClient
import logging

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CIDRS_TO_DELETE = ["100.78.64.0/19"]  # CIDRs to remove
OUTPUT_FILE = "nsg_cleanup_log.txt"

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(OUTPUT_FILE, mode="a"),
        logging.StreamHandler()
    ]
)

# ---------------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------------
def delete_cidr_from_nsg_rules():
    """Removes specified CIDRs from NSG rules across all accessible subscriptions."""
    credential = AzureCliCredential()
    subscription_client = SubscriptionClient(credential)

    logging.info("Starting NSG cleanup process...")
    logging.info(f"CIDRs to remove: {CIDRS_TO_DELETE}")

    for sub in subscription_client.subscriptions.list():
        subscription_id = sub.subscription_id
        network_client = NetworkManagementClient(credential, subscription_id)

        # List all NSGs in this subscription
        for nsg in network_client.network_security_groups.list_all():
            nsg_name = nsg.name
            rg_name = nsg.id.split("/")[4]

            # Get NSG security rules
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
                        logging.info(f"✅ Updated rule '{rule.name}' in NSG '{nsg_name}' (removed {CIDRS_TO_DELETE})")
                    except Exception as e:
                        logging.error(f"❌ Failed to update rule '{rule.name}' in NSG '{nsg_name}': {e}")

    logging.info("NSG cleanup completed successfully!")

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    delete_cidr_from_nsg_rules()