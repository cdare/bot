import requests
import logging
import json

class JIRAClient:
    
    def __init__(self, url, auth):
        self.url = url
        self.auth = auth

    def _request(self, query, method="GET", payload={}):
        headers = {'Authorization':'Basic '+self.auth,"Content-Type": "application/json"}
#        print(self.url+query)
#       print(payload)
        r = requests.request(method, self.url+query, headers=headers, data=payload,verify=False)
        if(r.status_code != requests.codes.ok):
#            print(r.text)
            r.raise_for_status()
        return r.json()

    def filter(self,id):
        r = self._request("filter/" + str(id))
        return r.get("jql")

    def search(self, filter_id):
        jql = self.filter(filter_id)
        data = {'jql':jql,'maxResults':10, 'startAt':0}
        issues = self._request("search/", method="POST", payload=json.dumps(data))
        return issues
