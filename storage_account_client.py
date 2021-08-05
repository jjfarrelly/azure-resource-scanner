from azure.mgmt.storage import StorageManagementClient
from azure.identity import AzureCliCredential



class storage_scanner():
    def __init__(self):
        self.credentials = AzureCliCredential()

    def search_public_storage_accounts(self, resource_group, subscription_id):
        self.subscription_id = subscription_id
        self.storage_client = StorageManagementClient(self.credentials, self.subscription_id)
        storage_accounts_for_remediation = []
        storage_accounts = self.storage_client.storage_accounts.list_by_resource_group(resource_group)
        for storage_account in storage_accounts:
            if storage_account.allow_blob_public_access == True:
                storage_accounts_for_remediation.append(storage_account)
        return storage_accounts_for_remediation
    
    def search_http_enabled_storage_accounts(self, resource_group, subscription_id):
        self.subscription_id = subscription_id
        self.storage_client = StorageManagementClient(self.credentials, self.subscription_id)
        storage_accounts_for_remediation = []
        storage_accounts = self.storage_client.storage_accounts.list_by_resource_group(resource_group)
        for storage_account in storage_accounts:
            if storage_account.enable_https_traffic_only == False:
                storage_accounts_for_remediation.append(storage_account)
        return storage_accounts_for_remediation