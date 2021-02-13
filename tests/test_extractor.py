import os
import sys
import pickle
import json
from pathlib import Path
from redminelib import Redmine, exceptions
sys.path.append(str(Path(__file__).resolve().parent.parent))
from extractor import IssueExtractor
import unittest
from unittest.mock import patch, Mock

def mocked_redmine(*args, **kwargs):

    class MockRedmine:
        def __init__(self, url, key=kwargs['key']):
            print("::MockRedmine initialized, url:%s" % (url))
            # Create the dummy redmine object to create other data
            self.__redmine = Redmine(url, key=kwargs['key'])
            assert self.__redmine != None, "Redmine instance should be created."

            self.project = MockProjects(self.__redmine)
            self.issue = MockIssues(self.__redmine, self.project)

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
            # pj.id = 1   -> Impossible to set read only attribute
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
            issue1 = self.__redmine.issue.new()
            issue2 = self.__redmine.issue.new()

            issues = [issue1, issue2]
            print("::Mock issue list created: %s" % issues)
            return issues

        def get(self, issue_id, include):
            print("::MockIssues#get called, issue_id: %d" % issue_id)
            issue = self.__redmine.issue.new()
            # issue.id = issue_id  -> Impossible to set read only attribute
            issue.project_id = "myproject"
            issue.subject = ('issue_%d' % issue_id)
            issue.description = '_abc_'
            issue.status_id = 3

            # print("::Mock issue created: %s" % vars(issue))
            print("::Mock issue created: %s" % issue)
            return issue

    return MockRedmine(args[0], key=kwargs['key'])

# Test class
class TestRedmineResponse(unittest.TestCase):
 
    @patch('extractor.Redmine', side_effect=mocked_redmine)
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

        # Issue detail #0
        issue = ie.fetch_issue_detail(0)
        # print(issue)
        self.assertEqual("issue_0", issue.subject)
        self.assertEqual("_abc_", issue.description)
        self.assertEqual(3, issue.status_id)

        # Issue detail #1
        issue = ie.fetch_issue_detail(1)
        self.assertEqual("issue_1", issue.subject)

        self.assertEqual(1, mock_get.call_count)
        API_KEY = os.environ.get("REDMINE_API_KEY")
        mock_get.assert_called_with('http://localhost/redmine/', key=API_KEY)
        # print(mock_get.mock_calls)

if __name__ == '__main__':
    unittest.main()