import unittest
from jira_client import JIRAClient
import marvin 
import os
import json
import logging
import sys
import configparser
import base64

class JIRABotTestCase(unittest.TestCase):
    
    def setUp(self):
        config = configparser.ConfigParser()
        config.read("marvin_tests_config.ini")
        jconfig = config["JIRA"]
        
        #establish save file
        path = os.path.dirname(os.path.realpath(__file__))
        self.store = path+config["DB"]["save_file"] 
        
        #setup JIRA Client
        auth_s = "{0}:{1}".format(jconfig["username"],jconfig["password"]).encode("ascii")
        basic = base64.b64encode(auth_s).decode("ascii")
        self.jira_client = JIRAClient(
            url=jconfig["url"],
            auth=basic,
            username=jconfig["username"])
                  
        self.filter_id = jconfig["filter_id"]        
        self.test_issue_id=jconfig["test_issue"]
        #clear all the comments in the test issue
        comments = self.jira_client.get_comments(self.test_issue_id)
        #for c in comments["comments"]:
            #c_id = c["id"]
            #self.jira_client.delete_comment(c_id)
    
    def tearDown(self):
        if(os.path.isfile(self.store)):
            os.remove(self.store)

    def test_get_queue(self):
        queue = marvin.get_queue(self.store)
        self.assertIsNotNone(queue)
        self.assertIsNotNone(queue["issues"])

    def test_save_queue(self):
        issues = ["8929292","22113"]
        marvin.save_queue(issues, self.store)
        queue = marvin.get_queue(self.store)
        self.assertEqual(issues,queue['issues'])
    
    def test_get_new_issues(self):
      
        issues = marvin.get_issues(self.jira_client, self.filter_id)

        #get newest
        newest = marvin.get_latest_issue_in_queue(issues)
        #if the queue is empty
        if newest==False:
            even_newer=1
        else:
            even_newer = str(int(newest)+100)
        latest_issues = issues + [even_newer]
        new = marvin.find_new_issues(issues,latest_issues)
        self.assertNotIn(new,issues)
 
    def test_watching_new_issues(self):
        issues = marvin.get_issues(self.jira_client, self.filter_id)
        queue = marvin.get_queue(self.store)
        new = marvin.find_new_issues(current=queue,latest=issues)
        marvin.watch_issues(new)
        for i in issues:
            watchers = marvin.get_watchers(i)
            self.assertIn(user_id,watchers)
    
    def test_remove_watcher(self):
        response = self.jira_client.watch_issue("ISC-87")
        self.assertTrue(response)
        response = self.jira_client.unwatch_issue("ISC-87")
        self.assertTrue(response)
    
    def test_add_watcher(self):
        response = self.jira_client.unwatch_issue("ISC-87")
        self.assertTrue(response)
        response = self.jira_client.watch_issue("ISC-87")
        self.assertTrue(response)
    
    def test_comment(self):
        response = self.jira_client.add_comment("ISC-87","this is a test")
        self.assertIsNotNone(response["id"])
        response = self.jira_client.delete_comment("ISC-87", response["id"])
        self.assertTrue(response)

    def test_handle_empty_save_file(self):
        f = open(self.store, "w")
        f.write("")
        f.close()
        queue = marvin.get_queue(self.store)
        self.assertIsNotNone(queue)
        self.assertIsNotNone(queue["issues"])

#logging.basicConfig(level="INFO",stream=sys.stdout)

suite = unittest.TestLoader().loadTestsFromTestCase(JIRABotTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
