from jira_client import JIRAClient
import json
import os
import logging
import sys
import configparser
import base64

CONFIG_FILE="config.ini"

def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config
    
def add_issues_to_queue(issues):
    #get queue from storage
    queue = get_queue()
    
    
def save_queue(queue,fl):
    f = open(fl, "w")
    logging.info("Saving file to "+fl)
    save = {"issues":queue}
    f.write(json.dumps(save))
    f.close()

def get_queue(fl):
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
    search = jira_client.search(filter_id)

    #check top issue: if greater than I then add to bot queue
    issue_ids=[issue["id"] for issue in search["issues"]]
    logging.info("Got following issues from JIRA "+", ".join(issue_ids))
    return issue_ids    

def get_client(jconfig):
    auth_s = "{0}:{1}".format(jconfig["username"],jconfig["password"]).encode("ascii")
    basic = base64.b64encode(auth_s).decode("ascii")
    JC = JIRAClient(
        url=jconfig["url"], 
        auth=basic, 
        username=jconfig["username"])
    return JC

if __name__ == "__main__":
    
    config = load_config(CONFIG_FILE)
    jconfig = config["JIRA"]    
    save_path = os.path.dirname(os.path.abspath(__file__))+"/"+config["DB"]["save_file"]

    logging.basicConfig(level="INFO",stream=sys.stdout)
    
    comment = jconfig["message"] 
    
    JC = get_client(jconfig)    
    issues_ids=get_issues(JC, jconfig["filter_id"])
    issues_queue = get_queue(save_path)
         
    new = find_new_issues(issues_queue["issues"],issues_ids)
    print(new)
    for issue in new:
        #JC.watch_issue(issue)
        #JC.add_comment(issue, comment)
        issues_queue['issues'].insert(0, issue)    
        #save_queue(issues_queue['issues'], save_path)


