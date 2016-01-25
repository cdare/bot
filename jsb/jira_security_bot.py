from jira_client import JIRAClient
import json
import os
import logging
import sys

JIRA_URL = "https://jira.just-eat.net/rest/api/2/"
AUTH = ""
FILE = "resources/issue_queue.json"
USER = ""
FILTER = "16075"

def add_issues_to_queue(issues):
    #get queue from storage
    queue = get_queue()
    
    
def save_queue(queue, fl = FILE):
    f = open(fl, "w")
    logging.info("Saving file to "+fl)
    save = {"issues":queue}
    f.write(json.dumps(save))
    f.close()

def get_queue(fl=FILE):
    noexist=False
    queue = None
    try:
        logging.info("Will open file at "+fl+ "for reading queue")
        f = open(fl, "r")
        text = f.read()
        if(text == ""):
            raise FileNotFoundError()
        queue = json.loads(text)
    except FileNotFoundError as e:
        logging.info("No file found, will have to create one")
        noexist=True
        pass
    if(queue=="" or noexist):             
        logging.info("Initiating an empty queue")
        queue = {"issues":[]}
    
    logging.info("Got following issues from DB ["+", ".join(queue["issues"])+"]")
    return queue

def get_latest_issue_in_queue(queue):
    if len(queue)==0:
        return False
    queue.sort()
    return queue[len(queue)-1]

def find_new_issues(current,latest):
    latest_issue = get_latest_issue_in_queue(current)
    if(latest_issue==False):
        return latest
    new_issues = []
    for l in latest:
        if (l not in current and l > latest_issue):
            new_issues.append(l)  
    return new_issues

def watch_issues(jira_client, issues_to_watch):
    for i in issues_to_watch:
        jira_client.watch_issue(i)
        jira_client.comment(i)

def get_issues(jira_client, filter_id):

    #Get filter then pull search string
    search = jira_client.search(FILTER)

    #check top issue: if greater than I then add to bot queue
    issue_ids=[issue["id"] for issue in search["issues"]]
    logging.info("Got following issues from JIRA "+", ".join(issue_ids))
    return issue_ids    

if __name__ == "__main__":
    
   
    save_path = os.path.dirname(os.path.abspath(__file__))+"/"+FILE

    logging.basicConfig(level="INFO",stream=sys.stdout)
    
    comment = "This issue is being watchet by the JIRA Security bot as it containts a relevant term. If you feel this is in error, email security@just-eat.com"
    JC = JIRAClient(url="https://jira.just-eat.net/rest/api/2/", auth=AUTH, username=USER)
    
    issues_ids=get_issues(JC, FILTER)
    issues_queue = get_queue(save_path)
         
    new = find_new_issues(issues_queue["issues"],issues_ids)
    print(new)
    for issue in new:
        JC.watch_issue(issue)
        JC.add_comment(issue, comment)
        issues_queue['issues'].insert(0, issue)    
    save_queue(issues_queue['issues'], save_path)
    #bot adds itself as watcher to issues in queue, leaves comment


