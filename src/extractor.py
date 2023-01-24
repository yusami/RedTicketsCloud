# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import pickle
from pathlib import Path
from dotenv import load_dotenv
from redminelib import Redmine, exceptions
from src.utils import setup_folder
import logging
from functools import wraps

def my_log(logger):
    # decorator for logger
    def decorator_fn(fn):
        @wraps(fn)
        def wrap_fn(*args, **kwargs):
            local_args = locals()
            logger.debug(f"{fn.__name__} is called: {str(local_args)}")
            return_val = fn(*args, **kwargs)
            logger.debug(f"{fn.__name__} is complete: {str(return_val)}")
            return return_val
        return wrap_fn
    return decorator_fn

class IssueExtractor:
    __redmine = None

    def __init__(self):
        # logger
        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s")
        handler.setFormatter(fmt)
        self.__logger.addHandler(handler)

        # config
        self.load_config()

    def load_config(self):
        assert self.__logger is not None, "logger should be created."
        self.__logger.debug("%s is called" % sys._getframe().f_code.co_name)

        # Redmine configs
        load_dotenv(verbose=True)
        API_KEY = os.environ.get("REDMINE_API_KEY")
        assert API_KEY is not None, "Redmine api key should be configured."

        redmine_url = "http://localhost/redmine/"
        config_file = Path('config/projects.json')
        if config_file.exists():
            self.__logger.debug("Read the config file: %s" % config_file)
            with open(config_file, 'r', encoding='utf-8') as f:
                df = json.load(f)
            # Read Redmine url
            redmine_url = df.get("redmine.url", redmine_url)

        # create Redmine instance to call API
        self.__logger.debug("url: %s" % redmine_url)
        self.__redmine = Redmine(redmine_url, key=API_KEY)
        assert self.__redmine is not None, "Redmine instance should be created."

    def fetch_projects(self):
        """
        Fetch the list of projects from Redmine.

        Returns
        ----------
        projects : List of projects
            List of Redmine projet resource
        """
        assert self.__redmine is not None, "Redmine instance should be created."

        # Output directory
        data_dir = Path("data")

        projects = []
        offset = 0
        step = 50
        while True:
            try:
                self.__logger.debug("Fetching projects, offset: %d" % (offset))
                pjs = self.__redmine.project.all(offset=offset, limit=step)
                # print("List all projects: %s" % projects)
                if len(pjs) == 0:
                    break
                projects.extend(pjs)
                offset += len(pjs)
                # Relax as Redmine server need short break;-p
                time.sleep(0.1)
            except exceptions.ResourceNotFoundError as ex:
                # An exception may be thrown if an communication error occurs.
                print(type(ex))
                print(ex)
                break

        for project in projects:
            self.__logger.debug("Project identifier: %s" % (project.identifier))
            # Dump data
            project_dir = data_dir.joinpath(project.identifier)
            project_dir.mkdir(parents=True, exist_ok=True)

            project_file = project_dir.joinpath("project.pickle")
            self.__logger.debug("Write project: %s" % project_file)
            with open(project_file, "wb") as f:
                pickle.dump(project, f)
            issuefile = project_dir.joinpath("project.json")
            with open(issuefile, "w", encoding="utf-8") as f:
                f.write(json.dumps(list(project), indent=2, ensure_ascii=False))
        return projects

    @my_log(logging.getLogger(__file__))
    def fetch_issue_list(self, project):
        """
        Fetch the list of issue ID from Redmine project.

        Parameters
        ----------
        project : Project
            Redmine resource to fetch

        Returns
        ----------
        ids : list of int
            List of issue ID
        """
        assert self.__redmine is not None, "Redmine instance should be created."
        self.__logger.debug("Fetch issue list for project: %s" % (project.identifier))

        ids = []
        offset = 0
        step = 50
        while True:
            try:
                # Fetch id list from Redmine
                self.__logger.debug("Fetch issue list by offset: %d" % (offset))
                issues = self.__redmine.issue.filter(project_id=project.id, subproject_id="!*", offset=offset, limit=step, status_id="*", sort='id:asc')
                if len(issues) == 0:
                    break
                for issue in issues:
                    ids.append(issue.id)
                offset += len(issues)
                # Relax as Redmine server need short break;-p
                time.sleep(0.1)
            except exceptions.ResourceNotFoundError as ex:
                # An exception may be thrown if an communication error occurs.
                print(type(ex))
                print(ex)
                break
        return ids

    def fetch_issue_detail(self, issue_id):
        """
        Fetch the issue data from Redmine.

        Parameters
        ----------
        issue_id : int
            Issue id of Redmine

        Returns
        ----------
        issue : Redmine issue data 
            Redmine issue resource
        """
        assert self.__redmine is not None, "Redmine instance should be created."
        assert type(issue_id) == int, "Issue id should be int."

        # Fetch issue detail
        issue = self.__redmine.issue.get(issue_id, include=['changesets', 'journals'])
        # print("%d:%s (%s)" % (issue.id, issue.subject, issue.created_on))
        # print("id: %d, " % (issue.id), end="")
        # self.__logger.debug("%d:%s (%s)" % (issue.id, issue.subject, issue.created_on))
        return issue

    def fetch_issues_for_project(self, project):
        """
        Fetch the issue data from Redmine and export it

        Parameters
        ----------
        project : Project
            Redmine resource to fetch
        """
        assert self.__redmine is not None, "Redmine instance should be created."
        assert project is not None, "Redmine project should be given."

        # Output directory
        data_dir = Path("data").joinpath(project.identifier)
        issue_dir = data_dir.joinpath("issues")
        issue_dir.mkdir(parents=True, exist_ok=True)

        # Fetch ids of all issues for the project
        issue_list = self.fetch_issue_list(project)

        self.__logger.debug("Fetch issue detail...")
        issues = []
        i = 0
        for issue_id in issue_list:
            # Fetch the description and notes of the issue
            issue = self.fetch_issue_detail(issue_id)
            issues.append(issue)
            # Export the issue
            issuefile = issue_dir.joinpath(str(issue_id) + ".json")
            with open(issuefile, "w", encoding="utf-8") as f:
                f.write(json.dumps(list(issue), indent=2, ensure_ascii=False))
            i += 1
            if i%10 == 0:
                self.__logger.debug("issues: %d" % i)
        self.__logger.debug("...done")

        # Export issues data
        dumpfile = data_dir.joinpath("issues.pickle")
        self.__logger.debug("Write issues: %s" % dumpfile)
        with open(dumpfile, "wb") as f:
            pickle.dump(issues, f)

    def export_issues(self):
        """
        Write all issue data to files
        """
        # Clean up the folder before run
        data_dir = Path("data")
        setup_folder(data_dir)

        # Fetch all projcts
        projects = self.fetch_projects()
        for project in projects:
            # Export issues for the project
            self.fetch_issues_for_project(project)

if __name__ == "__main__":
    ie = IssueExtractor()
    ie.export_issues()
