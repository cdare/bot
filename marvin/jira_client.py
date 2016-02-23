import requests
import logging
import json

class JIRAClient:
    
    def __init__(self, url, auth, username):
        self.url = url
        self.auth = auth
        self.username = username

    def _request(self, query, method="GET", payload={}):
        headers = {'Authorization':'Basic '+self.auth,"Content-Type": "application/json"}
#        print(self.url+query)
#       print(payload)
        r = requests.request(method, self.url+query, headers=headers, data=payload,verify=False)
        if(r.status_code != requests.codes.ok):
#            print(r.text)
            r.raise_for_status()
        if(r.status_code == 204):
            return True
        else:
            return r.json()

    def filter(self,id):
        r = self._request("filter/" + str(id))
        return r.get("jql")

    def search(self, filter_id):
        jql = self.filter(filter_id)
        data = {'jql':jql,'maxResults':200, 'startAt':0}
        issues = self._request("search/", method="POST", payload=json.dumps(data))
        return issues

    def watch_issue(self, issue_id):
        post_data = self.username  
        response = self._request("issue/"+issue_id+"/watchers/", method="POST", payload=json.dumps(post_data))
        return response

    def unwatch_issue(self, issue_id):
        response = self._request("issue/"+issue_id+"/watchers/?username="+self.username, method="DELETE")
        return response

    def add_comment(self, issue_id, comment):
        data = {'body':comment}
        response = self._request("issue/"+issue_id+"/comment/", payload=json.dumps(data),method="POST")
        return response
         
    def delete_comment(self, issue_id, comment_id):
        response = self._request("issue/"+issue_id+"/comment/"+comment_id, method="DELETE")
        return response
       
    def get_comments(self,issue_id):
        response = self._request("issue/"+issue_id+"/comment/")
        return response
         


