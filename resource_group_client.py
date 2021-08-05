from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient



class resource_group_finder():
    def __init__(self, subscription_id):
        self.subscription_id = subscription_id
        self.credentials = AzureCliCredential()
        self.resource_client = ResourceManagementClient(self.credentials, self.subscription_id)

    def get_resource_groups(self):
        group_list = self.resource_client.resource_groups.list()
        resource_group_names = []
        for group in list(group_list):
            resource_group_names.append(group.name)

        return resource_group_names
                