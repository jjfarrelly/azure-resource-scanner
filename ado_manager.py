import json
import os 
import requests
import re
import time
from subscription_client import *

class ado_data_builder():
    def __init__(self, resource, theme):
        self.resource = resource
        self.theme = theme

    def extract_resource_data(self):
        self.name = self.resource.name
        match = re.search(r'(?:.*?\/){2}([^\/?#]+)', self.resource.id)
        self.sub_id = match.group(1)
        match = re.search(r'(?:.*?\/){4}([^\/?#]+)', self.resource.id)
        self.resource_group = match.group(1)
        sub_client = subscription_finder()
        self.sub_name = sub_client.get_subscription_name(self.sub_id)

    def build_ticket_data(self):
        data = {}
        data['THEME'] = self.theme
        data['NAME'] = self.name
        data['SUBSCRIPTION'] = self.sub_name
        data['RESOURCE GROUP'] = self.resource_group
        data['DESCRIPTION'] = self.theme+" - "+self.name+", Subscription - "+self.sub_name+", Resource Group - "+self.resource_group
        return data

class ado_restapi():
    def __init__(self, organization_name, project_id, ado_personal_access_token):
        self.personal_access_token = ado_personal_access_token
        self.organization_name = organization_name
        self.project_id = project_id
        self.ado_url = 'https://dev.azure.com/{}}/{}/_apis/wit/workitems/'.format(self.organization_name, self.project_id)
        print(self.ado_url)

    def create_work_item(self, work_item_type, work_item_title):

        item = '${}?api-version=6.0'.format(work_item_type)
        work_item_ado_url = '{}{}'.format(self.ado_url, item)

        data = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": work_item_title
            },
            {
                "op": "add",
                "path": "/fields/System.State",
                "value": "To Do"
            },
            {
                "op": "add",
                "path": "/fields/System.WorkItemType",
                "value": work_item_type
            }
        ]

        res = requests.post(work_item_ado_url, json=data, 
            headers={'Content-Type': 'application/json-patch+json'},
            auth=('', self.personal_access_token))
        
        return(res)

    def create_task(self, resource):
        resource_type = resource['THEME']
        task_title = resource_type+": "+resource['NAME']
        subscription = resource['SUBSCRIPTION']
        resource_group = resource['RESOURCE GROUP']
        description = resource['DESCRIPTION']

        task_ado_url = '{}{}'.format(self.ado_url, '$Task?api-version=6.0')

        data = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": task_title
            },
            {
                "op": "add",
                "path": "/fields/System.State",
                "value": "To Do"
            },
            {
                "op": "add",
                "path": "/fields/System.WorkItemType",
                "value": "Task"
            },
            {
                "op": "add",
                "path": "/fields/System.Description",
                "value": description
            },
            {
                "op": "add",
                "path": "/fields/System.Tags",
                "value": subscription+"; "+resource_group+"; "+resource_type+"; "
            }
        ]

        res = requests.post(task_ado_url, json=data, 
            headers={'Content-Type': 'application/json-patch+json'},
            auth=('', self.personal_access_token))
        return res
    
    def link_parent_to_task(self, task_id, task_rev, work_item_url):
        task_link_ado_url = '{}{}{}'.format(self.ado_url, task_id,'?api-version=6.0')
        data = [
            {
                "op": "test",
                "path": "/rev",
                "value": task_rev
            },
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": work_item_url,
                    "attributes": {
                        "comment": "link parent WIT"
                    }
                }
            }
        ]

        res = requests.patch(task_link_ado_url, json=data, 
            headers={'Content-Type': 'application/json-patch+json'},
            auth=('', self.personal_access_token))
        
        return res

    def link_owner_to_work_item(self, work_item_id, task_rev, work_item_owner):

        task_link_ado_url = '{}{}{}'.format(self.ado_url, work_item_id,'?api-version=6.0')
        print(task_link_ado_url)
        data = [
            {
                "op": "test",
                "path": "/rev",
                "value": task_rev
            },
            {
                "op": "add",
                "path": "/fields/System.AssignedTo",
                "value": work_item_owner
            }
        ]

        res = requests.patch(task_link_ado_url, json=data, 
            headers={'Content-Type': 'application/json-patch+json'},
            auth=('', self.personal_access_token))
        
        return res


class ado_manager():
    def __init__(self, organization_name, organization_id, project_id, ado_personal_access_token):
        self.organization_name = organization_name
        self.organization_id = organization_id
        self.project_id = project_id
        self.ado_restapi = ado_restapi(organization_name,project_id, ado_personal_access_token)
    
    def create_new_backlog_item_hierarchy(self, work_item_type, work_item_title, work_item_owner, resource_data):
        res = self.ado_restapi.create_work_item(work_item_type, work_item_title)
        res_json = res.json()
        print(res_json)
        work_item_id = res_json['id']
        work_item_rev = res_json['rev']

        res = self.ado_restapi.link_owner_to_work_item(work_item_id, work_item_rev, work_item_owner)
        work_item_url = 'https://bupatestpractice.visualstudio.com/{}/_apis/wit/workItems/{}'.format(self.organization_id, work_item_id)
        
        count = 0
        ticket_num = 1
        for resource in resource_data:

            res = self.ado_restapi.create_task(resource)
            print("-----------------------------------")
            print("Created ticket number: "+str(ticket_num))
            print("work_item_id: "+str(work_item_id))
            print("work_item_rev: "+str(work_item_rev))
            print("-----------------------------------")

            res_json = res.json()
            task_id = res_json['id']
            task_rev = res_json['rev']
            res = self.ado_restapi.link_parent_to_task(task_id, task_rev, work_item_url)
            count += 1
            ticket_num += 1

            if count % 3 == 0:
                time.sleep(5)
        print(str(count)+" tasks have been created under Product Backlog Item: "+work_item_title)


class az_devops_creator():
    def __init__(self, ado_organization_name, ado_organization_id, ado_project, ado_personal_access_token):
        self.ado_organization_name = ado_organization_name
        self.ado_organization_id = ado_organization_id
        self.ado_project = ado_project
        self.ado_personal_access_token = ado_personal_access_token
        self.ado_manager = ado_manager(self.ado_organization_name, self.ado_organization_id, self.ado_project, self.ado_personal_access_token)
    
    def new_backlog_item_with_tasks(self, work_item_type, work_item_title, work_item_owner, resource_data):
        self.ado_manager.create_new_backlog_item_hierarchy(work_item_type, work_item_title, work_item_owner, resource_data)




