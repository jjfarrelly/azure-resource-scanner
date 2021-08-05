from disk_client import disk_scanner
from ip_client import ip_scanner
from storage_account_client import storage_scanner
from resource_group_client import resource_group_finder
from subscription_client import subscription_finder
from ado_manager import ado_data_builder
from ado_manager import az_devops_creator
from ado_manager import ado_manager
import pyfiglet

print("Starting...")
ascii_banner = pyfiglet.figlet_format("Welcome to Azure Resource Scanner")
print(ascii_banner)

# Required variables for Azure DevOps API
ado_personal_access_token = input("ADO Personal Access Token: ")
ado_organization_name = input("ADO Organization Name: ")
ado_organization_id = input("ADO Organization ID: ")
ado_project = input("ADO Project Name: ")

print("Please choose your ADO work item type")
print(" - Issue [1] ")
print(" - Product Backlog Item [2] ")
ans = input("Enter number: ")
if ans == "1":
    work_item_type = "Product Backlog Item"
elif ans == "2":
    work_item_type = "Issue" 

## Retrieves list of all subscriptions to scan through
subscription_client = subscription_finder()
subscription_ids = subscription_client.get_subscription_ids()
print("I have found "+str(len(subscription_ids))+" subscription")


# Query type selection
print("Resource Type Queries")
print("----------------------")
print(" - Unattached Disks [1] ")
print(" - Reserved Disks [2] ")
print(" - Disk public endpoints [3] ")
print(" - Public Ips [4] ")
print(" - Public Storage Accounts [5] ")
print(" - HTTP enabled Storage Accounts [6]")
print("----------------------")

ans = input("Enter number of resource type you would like to query for: ")
if ans == "1":
    theme = "Managed Disk"
    query = "unattached disk"
    scanner = disk_scanner()
elif ans == "2":
    theme = "Managed Disk"
    query = "reserved disk"
    scanner = disk_scanner()
elif ans == "3":
    theme = "Managed Disk"
    query = "public disk"
    scanner = disk_scanner()
elif ans == "4":
    theme = "Public IP"
    query = "public ip"
    scanner = ip_scanner()
elif ans == "5":
    theme = "Storage Account"
    query = "public storage account"
    scanner = storage_scanner()
elif ans == "6":
    theme = "Storage Account"
    query = "HTTP enabled storage account"
    scanner = storage_scanner()


print("----------------------------")
# Initialise empty list of non compliant resource to add to if found
non_compliant_resources = []
for subscription_id in subscription_ids:
    print("---------------------------------")
    subscription_name = subscription_client.get_subscription_name(subscription_id)
    print("Scanning subscription "+ subscription_name)
    print("---------------------------------")
    print("Collecting resource groups in subscription")
    resource_group_client = resource_group_finder(subscription_id)
    resource_groups = resource_group_client.get_resource_groups()
    print("I have found "+str(len(resource_groups))+" resource groups")
    print("---------------------------------")
    for resource_group in resource_groups:

        print("Scanning : "+resource_group)
        if query == "unattached disk":
            resources = scanner.search_unattached_disks(resource_group,subscription_id)
        elif query == "public disk":
            resources = scanner.search_public_disks(resource_group, subscription_id)
        elif query == "reserved disk":
            resources = scanner.search_reserved_disks(resource_group, subscription_id)
        elif query == "public ip":
            resources = scanner.search_public_ips(resource_group, subscription_id)
        elif query == "public storage account":
            resources = scanner.search_public_storage_accounts(resource_group, subscription_id)
        elif query == "HTTP enabled storage account":
            resources = scanner.search_http_enabled_storage_accounts(resource_group, subscription_id)
        
        if resources:
            for resource in resources:
                print("---------------------------------")
                print("Non compliant "+query+" found: "+resource.name)
                print("---------------------------------")
                # Add non compliant resource to list
                non_compliant_resources.append(resource)

print("I have found "+str(len(non_compliant_resources))+" "+query+" resources throughout the "+str(len(subscription_ids))+" subscription(s) scanned")
ans = input("Would you like to build new Azure DevOps tickets for these non compliant resources? y/n " )
if ans == "y":
    ado_manager = ado_manager(ado_organization_name, ado_organization_id, ado_project, ado_personal_access_token)
    
    # Build ADO ticket data
    resource_data = []
    for resource in non_compliant_resources:
        builder = ado_data_builder(resource, theme)
        builder.extract_resource_data()
        resource_data.append(builder.build_ticket_data())

    # Inputs for work item 
    pb_item_title_input = input("Enter a title for your new ADO work item: ")
    pb_item_owner_input = input("Enter an owner for your new ADO work item: ")
    print("Creating your tickets...")

    # creates a backlog work item with associated child tasks
    az_devops_creator = az_devops_creator(ado_organization_name, ado_organization_id, ado_project, ado_personal_access_token)
    az_devops_creator.new_backlog_item_with_tasks(work_item_type, pb_item_title_input, pb_item_owner_input, resource_data)
    print("Auto discovery and ticket creation complete")
