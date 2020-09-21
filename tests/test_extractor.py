import sys
import pickle
import json
from pathlib import Path
from redminelib import Redmine, exceptions
import redminelib
sys.path.append(str(Path(__file__).resolve().parent.parent))
from extractor import IssueExtractor
import unittest
from unittest import mock

def mocked_redmine(*args, **kwargs):
    class MockRedmine:
        def __init__(self, url, api_key):
            print("::MockRedmine initialized, url:%s, key:%s" % (url, api_key))
            self.__redmine = Redmine(url, key=api_key)
            self.project = MockProjects(self.__redmine)
            self.issue = MockIssues(self.__redmine, self.project)

    class MockProjects:
        def __init__(self, redmine):
            print("::MockProjects initialized")
            self.__redmine = redmine
        
        def all(self, offset, limit):
            print("::MockProjects#all called, offset: %d, limit: %d" % (offset, limit))
            if offset > 0:
                print("::No more project found")
                return []
            pj = self.__redmine.project.new()
            pj.identifier = 'darkside'
            # pj.id = 1   -> Impossible to set read only attribute
            pj.name = 'Darkside'
            pj.status = 2
            pj.description = "abc"

            # print("::Mock project created: %s" % vars(pj))
            print("::Mock project created: %s" % pj.identifier)
            projects = [pj]
            # self.issue = MockIssues(self.__redmine, pj)
            return projects

    class MockIssues:
        def __init__(self, redmine, project):
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
            issue.project_id = "darkside"
            issue.subject = ('dragon_%d' % issue_id)
            issue.description = '_abc_'
            issue.status_id = 3

            # print("::Mock issue created: %s" % vars(issue))
            print("::Mock issue created: %s" % issue)
            return issue

    return MockRedmine("http://foo/bar", "123")
 
# Test class
class TestRedmineResponse(unittest.TestCase):
 
    @mock.patch('extractor.Redmine', side_effect=mocked_redmine)
    def test_redmine_projects(self, mock_get):
        ie = IssueExtractor()

        # Project by mock
        projects = ie.fetch_projects()
        self.assertEqual(1, len(projects))
        project = projects[0]
        # print("::Received response: %s" % vars(project))
        # print(vars(project))
        self.assertEqual("darkside", project.identifier)
        self.assertEqual("Darkside", project.name)
        self.assertEqual("abc", project.description)
        self.assertEqual(2, project.status)

        # Issue list
        ids = ie.fetch_issue_list(project)
        print("::issue ids: %s" % ids)
        self.assertEqual(2, len(ids))

        # Issue detail #0
        issue = ie.fetch_issue_detail(0)
        # print(issue)
        self.assertEqual("dragon_0", issue.subject)
        self.assertEqual("_abc_", issue.description)
        self.assertEqual(3, issue.status_id)

        # Issue detail #1
        issue = ie.fetch_issue_detail(1)
        self.assertEqual("dragon_1", issue.subject)

if __name__ == '__main__':
    unittest.main()