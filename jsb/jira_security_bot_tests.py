import unittest
from jira_client import JIRAClient
import jira_security_bot
import os
import json
import logging
import sys

class JIRABotTestCase(unittest.TestCase):
    
    def setUp(self):
        path = os.path.dirname(os.path.realpath(__file__))
        self.store = path+'/resources/'+"test_queue.json" 
        self.jira_client = JIRAClient(url="https://jira.just-eat.net/rest/api/2/", auth="***REMOVED***",username="***REMOVED***")
        self.filter_id ="16075"        
        self.test_issue_id="ISC-87"
        #clear all the comments in the test issue
        comments = self.jira_client.get_comments(self.test_issue_id)
        #for c in comments["comments"]:
            #c_id = c["id"]
            #self.jira_client.delete_comment(c_id)
    
    def tearDown(self):
        if(os.path.isfile(self.store)):
            os.remove(self.store)

    def test_get_queue(self):
        queue = jira_security_bot.get_queue(self.store)
        self.assertIsNotNone(queue)
        self.assertIsNotNone(queue["issues"])

    def test_save_queue(self):
        issues = ["8929292","22113"]
        jira_security_bot.save_queue(issues, self.store)
        queue = jira_security_bot.get_queue(self.store)
        self.assertEqual(issues,queue['issues'])
    
    def test_get_new_issues(self):
      
        issues = jira_security_bot.get_issues(self.jira_client, self.filter_id)

        #get newest
        newest = jira_security_bot.get_latest_issue_in_queue(issues)
        #if the queue is empty
        if newest==False:
            even_newer=1
        else:
            even_newer = str(int(newest)+100)
        latest_issues = issues + [even_newer]
        new = jira_security_bot.find_new_issues(issues,latest_issues)
        self.assertNotIn(new,issues)
 
    def test_watching_new_issues(self):
        issues = jira_security_bot.get_issues(self.jira_client, self.filter_id)
        queue = jira_security_bot.get_queue(self.store)
        new = jira_security_bot.find_new_issues(current=queue,latest=issues)
        jira_security_bot.watch_issues(new)
        for i in issues:
            watchers = jira_security_bot.get_watchers(i)
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
        queue = jira_security_bot.get_queue(self.store)
        self.assertIsNotNone(queue)
        self.assertIsNotNone(queue["issues"])

#logging.basicConfig(level="INFO",stream=sys.stdout)

suite = unittest.TestLoader().loadTestsFromTestCase(JIRABotTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
