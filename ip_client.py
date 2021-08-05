from azure.mgmt.network import NetworkManagementClient
from azure.identity import AzureCliCredential
import re

class ip_scanner():
    def __init__(self):
        self.credentials = AzureCliCredential()

    def search_public_ips(self, resource_group, subscription_id):
        self.subscription_id = subscription_id
        self.network_client = NetworkManagementClient(self.credentials, self.subscription_id)
        public_ips_for_remediation = []
        public_ips = self.network_client.public_ip_addresses.list_all()
        for public_ip in list(public_ips):
            match = re.search(r'(?:.*?\/){4}([^\/?#]+)', public_ip.id)
            rg = match.group(1)
            if rg == resource_group:
                public_ips_for_remediation.append(public_ip)
        return public_ips_for_remediation

