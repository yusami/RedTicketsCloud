import os
import sys
import pickle
import json
from pathlib import Path
from redminelib import Redmine, exceptions
from src.extractor import IssueExtractor
import unittest
from unittest.mock import patch, Mock
import pprint

def mocked_redmine(*args, **kwargs):

    class MockRedmine:
        def __init__(self, url, key=kwargs['key']):
            assert url != None, "URL should be valid."

            print("::Initialize MockRedmine, url:%s" % (url))
            self.__redmine = Redmine(url, key=kwargs['key'])
            assert self.__redmine != None, "Redmine instance should be created."

            # Create the mock instances
            self.project = MockProjects(self.__redmine)
            assert self.project != None, "MockProjects instance should be created."

            projects = self.project.all(0, 0)
            assert projects != None, "Projects list should be valid."
            assert len(projects) > 0, "Projects list #0 should be valid."

            self.issue = MockIssues(self.__redmine, projects[0])
            assert self.issue != None, "Issues should be valid."

            print("::MockRedmine is initialized")

    class MockProjects:
        def __init__(self, redmine):
            assert redmine != None, "Redmine instance should be valid."

            print("::Initialize MockProjects")
            self.__redmine = redmine

            # Create the mock project
            self.__projects = []
            for i in range(1,3):
                pj = self.__redmine.project.new()
                pj.identifier = 'identifier_mock_%d' % i
                pj.name = 'name_mock_%d' % i
                pj.description = "description_mock_%d" % i
                pj.status = i
                self.__projects.append(pj)
                print("::Mock project is created: %s" % pj.identifier)
        
        def all(self, offset, limit):
            assert self.__projects != None, "Projects should be created."

            print("::MockProjects#all called, offset: %d, limit: %d" % (offset, limit))
            if offset > 0:
                print("::No more project found")
                return []

            return self.__projects

    class MockIssues:
        def __init__(self, redmine, project):
            assert redmine != None, "Redmine argv should be valid."
            assert project != None, "Project argv should be valid."
            assert project.identifier != None, "Project identifier should be valid."
            # pprint.pprint(vars(project))

            print("::Initialize MockIssues")
            self.__redmine = redmine

            # Create the dummy issues
            issues = []
            for i in range(1,3):
                issue = self.__redmine.issue.new()
                issue.project_id = project.identifier
                issue.subject = ('subject_%d' % i)
                issue.description = ('description_%d' % i)
                issue.status_id = (i * 2)
                issues.append( issue)
            print("::Mock issue list: %s" % issues)
            self.__issues = issues
        
        def all(self, project_id, offset, limit, sort, include):
            assert self.__issues != None, "Issues should be created."

            print("::MockIssues#all called, offset: %d, limit: %d" % (offset, limit))
            if offset > 0:
                print("::No more issue found")
                return []

            return self.__issues

        def filter(self, project_id, subproject_id, offset, limit, status_id, sort):
            assert self.__issues != None, "Issues should be created."

            print("::MockIssues#filter called, offset: %d, limit: %d" % (offset, limit))
            if offset > 0:
                print("::No more issue found")
                return []

            return self.__issues

        def get(self, issue_id, include):
            assert self.__issues != None, "Issues should be created."

            print("::MockIssues#get called, issue_id: %d" % issue_id)
            issue = None
            print( "::Issue list length: %d, issue id: %d" % (len(self.__issues), issue_id))
            if (0 < issue_id) and (issue_id <= len(self.__issues)):
                issue = self.__issues[ issue_id - 1 ]

            return issue

    return MockRedmine(args[0], key=kwargs['key'])

# Test class
class TestRedmineResponse(unittest.TestCase):
 
    @patch('src.extractor.Redmine', side_effect=mocked_redmine)
    def test_redmine_projects(self, mock_get):
        print("::%s called" % sys._getframe().f_code.co_name)
        ie = IssueExtractor()

        # Project list
        projects = ie.fetch_projects()
        self.assertEqual(2, len(projects))
        # print(vars(project))

        # Project detail
        for i in range(1,3):
            project = projects[ i-1 ]
            self.assertEqual("identifier_mock_%d" % i, project.identifier)
            self.assertEqual("name_mock_%d" % i, project.name)
            self.assertEqual("description_mock_%d" % i, project.description)
            self.assertEqual(i, project.status)

        # Issue list
        ids = ie.fetch_issue_list(projects[0])
        print("::Issue id list (ids are ignored): %s" % ids)
        self.assertEqual(2, len(ids))

        # Issue detail
        for i in range(1,3):
            issue = ie.fetch_issue_detail( i )
            self.assertEqual(("subject_%d" % i), issue.subject)
            self.assertEqual(("description_%d" % i), issue.description)
            self.assertEqual(i * 2, issue.status.id)
            # pprint.pprint(vars(issue))

        self.assertEqual(1, mock_get.call_count)
        API_KEY = os.environ.get("REDMINE_API_KEY")
        # mock_get.assert_called_with('http://localhost/redmine/', key=API_KEY)
        print(mock_get.mock_calls)

if __name__ == '__main__':
    unittest.main()