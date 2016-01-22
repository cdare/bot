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
        self.jira_client = JIRAClient(url="https://jira.just-eat.net/rest/api/2/", auth="***REMOVED***")
        self.filter_id ="16075"        

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
        queue = json.load(open(self.store, "r"))
        self.assertEqual(issues,queue)
    
    def test_get_new_issues(self):
      
        issues = jira_security_bot.get_issues(self.jira_client, self.filter_id)

        #get newest
        newest = jira_security_bot.get_latest_issue_in_queue(issues)
        if newest==False:
            even_newer=1
        else:
            even_newer = str(int(newest)+100)
        latest_issues.insert(0,even_newer)
        new = jira_security_bot.find_new_issues(issues,latest_issues)
        self.assertNotIn(new,issues)
 
    def test_watching_new_issues(self):
        jira_security_bot.set_store_path(self.store)
        issues = jira_security_bot.get_issues()
        new = jira_security_bot.find_new_issues(issues)
        jira_security_bot.watch_issues(new)
        for i in issues:
            watchers = jira_security_bot.get_watchers(i)
            self.assertIn(user_id,watchers)

logging.basicConfig(level="INFO",stream=sys.stdout)
suite = unittest.TestLoader().loadTestsFromTestCase(JIRABotTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
