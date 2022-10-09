import os
import sys
import pickle
import json
from pathlib import Path
from redminelib import Redmine, exceptions
sys.path.append(str(Path(__file__).resolve().parent.parent.joinpath("lib")))
from lib.extractor import IssueExtractor
import unittest
from unittest.mock import patch, Mock
import pprint

def mocked_redmine(*args, **kwargs):

    class MockRedmine:
        def __init__(self, url, key=kwargs['key']):
            print("::MockRedmine initialized, url:%s" % (url))
            # Create the dummy redmine object to create other data
            self.__redmine = Redmine(url, key=kwargs['key'])
            assert self.__redmine != None, "Redmine instance should be created."

            self.project = MockProjects(self.__redmine)
            self.issue = MockIssues(self.__redmine, self.project)
            print("::MockRedmine is initialized")

    class MockProjects:
        def __init__(self, redmine):
            assert redmine != None, "Redmine instance should be created."

            print("::MockProjects initialized")
            self.__redmine = redmine
        
        def all(self, offset, limit):
            print("::MockProjects#all called, offset: %d, limit: %d" % (offset, limit))
            if offset > 0:
                print("::No more project found")
                return []
            pj = self.__redmine.project.new()
            pj.identifier = 'myproject'
            pj.name = 'darkside'
            pj.status = 2
            pj.description = "abc"

            # print("::Mock project created: %s" % vars(pj))
            print("::Mock project created: %s" % pj.identifier)
            projects = [pj]
            # self.issue = MockIssues(self.__redmine, pj)
            return projects

    class MockIssues:
        def __init__(self, redmine, project):
            assert redmine != None, "Redmine instance should be created."

            print("::MockIssues initialized")
            self.__redmine = redmine
        
        def filter(self, project_id, subproject_id, offset, limit, status_id, sort):
            print("::MockIssues#filter called, offset: %d, limit: %d" % (offset, limit))
            if offset > 0:
                print("::No more issue found")
                return []

            issues = []
            for i in range(1,3):
                issue = self.__redmine.issue.new()
                issue.project_id = project_id
                issue.subject = ('subject_%d' % i)
                issue.description = ('description_%d' % i)
                issue.status_id = i * 2
                issues.append( issue )
                print("::Mock issue is created: %s" % issue)

            print("::Mock issue list: %s" % issues)
            return issues

        def get(self, issue_id, include):
            print("::MockIssues#get called, issue_id: %d" % issue_id)
            issue = self.__redmine.issue.new()
            issue.project_id = "myproject"
            issue.subject = ('subject_%d' % issue_id)
            issue.description = ('description_%d' % issue_id)
            issue.status_id = (issue_id * 2)
            # pprint.pprint(vars(issue))

            # print("::Mock issue is retrieved for id: %d, subject: %s" % (issue_id, issue.subject))
            return issue

    return MockRedmine(args[0], key=kwargs['key'])

# Test class
class TestRedmineResponse(unittest.TestCase):
 
    @patch('lib.extractor.Redmine', side_effect=mocked_redmine)
    def test_redmine_projects(self, mock_get):
        print("::%s called" % sys._getframe().f_code.co_name)
        ie = IssueExtractor()

        # Project by mock
        projects = ie.fetch_projects()
        self.assertEqual(1, len(projects))
        project = projects[0]
        # print("::Received response: %s" % vars(project))
        # print(vars(project))
        self.assertEqual("myproject", project.identifier)
        self.assertEqual("darkside", project.name)
        self.assertEqual("abc", project.description)
        self.assertEqual(2, project.status)

        # Issue list
        ids = ie.fetch_issue_list(project)
        print("::issue ids: %s" % ids)
        self.assertEqual(2, len(ids))

        # Issue detail
        for i in range(1,3):
            issue = ie.fetch_issue_detail( i )
            self.assertEqual(("subject_%d" % i), issue.subject)
            self.assertEqual(("description_%d" % i), issue.description)
            self.assertEqual(i * 2, issue.status.id)

        self.assertEqual(1, mock_get.call_count)
        API_KEY = os.environ.get("REDMINE_API_KEY")
        # mock_get.assert_called_with('http://localhost/redmine/', key=API_KEY)
        # print(mock_get.mock_calls)

if __name__ == '__main__':
    unittest.main()