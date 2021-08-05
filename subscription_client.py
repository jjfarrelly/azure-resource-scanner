from azure.identity import AzureCliCredential
from azure.mgmt.subscription import SubscriptionClient
import re



class subscription_finder():
    def __init__(self):
        self.credentials = AzureCliCredential()
        self.subscription_client = SubscriptionClient(self.credentials)

    def get_subscription_ids(self):
        sub_list = self.subscription_client.subscriptions.list()
        subscription_ids = []
        for sub in list(sub_list):
            match = re.search(r'(?:.*?\/){2}([^\/?#]+)', sub.id)
            sub_id = match.group(1)
            subscription_ids.append(sub_id)

        return subscription_ids

    def get_subscription_name(self, subscription_id):
        sub = self.subscription_client.subscriptions.get(subscription_id)
        return sub.display_name