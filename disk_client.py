from azure.mgmt.compute import ComputeManagementClient
from azure.identity import AzureCliCredential



class disk_scanner():
    def __init__(self):
        self.credentials = AzureCliCredential()

    def search_reserved_disks(self, resource_group, subscription_id):
        self.subscription_id = subscription_id
        self.compute_client = ComputeManagementClient(self.credentials, self.subscription_id)
        disks_for_remediation = []
        disks = self.compute_client.disks.list_by_resource_group(resource_group)
        for disk in disks:
            if disk.disk_state == "Reserved":
                disks_for_remediation.append(disk)
        return disks_for_remediation

    def search_unattached_disks(self, resource_group, subscription_id):
        self.subscription_id = subscription_id
        self.compute_client = ComputeManagementClient(self.credentials, self.subscription_id)
        disks_for_remediation = []
        disks = self.compute_client.disks.list_by_resource_group(resource_group)
        for disk in disks:
            if disk.disk_state == "Unattached":
                disks_for_remediation.append(disk)
        return disks_for_remediation

    def search_public_disks(self, resource_group, subscription_id):
        self.subscription_id = subscription_id
        self.compute_client = ComputeManagementClient(self.credentials, self.subscription_id)
        disks_for_remediation = []
        disks = self.compute_client.disks.list_by_resource_group(resource_group)
        for disk in disks:
            if disk.network_access_policy == 'AllowAll':
                disks_for_remediation.append(disk)
        return disks_for_remediation

