from jira_client import JIRAClient
import json
import os
import logging
import sys

JIRA_URL = "https://jira.just-eat.net/rest/api/2/"
AUTH = "***REMOVED***"
FILE = ""

def add_issues_to_queue(issues):
    #get queue from storage
    queue = get_queue()
    
    
def save_queue(queue, fl = FILE):
    f = open(fl, "w")
    f.write(json.dumps(queue))
    f.close()

def get_queue(fl=FILE):
    noexist=False
    queue = None
    try:
        logging.info("Will open file at "+fl+ "for reading queue")
        queue = json.load(open(fl, "r"))
    except FileNotFoundError as e:
        noexist=True
        pass
    if(queue=="" or noexist):             
        queue = {"issues":[]}
    return queue

def get_latest_issue_in_queue(queue):
    if len(queue)==0:
        return False
    queue.sort(reverse=True)
    return queue[0]

def find_new_issues(current,latest):
    latest_issue = get_latest_issue_in_queue(current)
    if(latest_issue==False):
        return latest
    new_issues = []
    for l in latest:
        if (l not in current and l > latest_issue):
            new_issues.append(l)  
    return new_issues

def get_issues(jira_client, filter_id):

    #Get filter then pull search string
    search = jira_client.search("16075")

    #check top issue: if greater than I then add to bot queue
    issue_ids={issue["id"] for issue in search["issues"]}
    return issue_ids    

if __name__ == "__main__":
    
    logging.basicConfig(level="INFO",stream=sys.stdout)

    JC = JIRAClient(url="https://jira.just-eat.net/rest/api/2/", auth="***REMOVED***")
    
    issues_ids=get_issues(JC, "16075")
    #get latest issue I from store and put ID in variable
    
    #print(issue_ids)
    add_issues_to_queue(issue_ids)
    #bot adds itself as watcher to issues in queue, leaves comment


