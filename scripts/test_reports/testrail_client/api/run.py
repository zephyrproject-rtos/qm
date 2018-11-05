#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class Run(TestRailAPIBase):
    """
    Use the following API methods to request details
    about test runs and to create or modify test runs.
    """
    def __repr__(self):
        return '<TestRailAPI run>'

    def get(self, run_id):
        """
        Returns an existing test run.
        :param run_id:The ID of the test run
        """
        return self._get('get_run/{}'.format(run_id))

    def for_project(self, project_id, **filters):
        """
        Returns a list of test runs for a project.
        Only returns those test runs that are not part of a test plan
        :param project_id:The ID of the project
        :param filters: dict, request filter
        """
        return self._get('get_runs/{}'.format(project_id),
                         params=filters)

    def add(self, project_id, suite_id=None, name=None,
            description=None, milestone_id=None, assignedto_id=None,
            include_all=True, case_ids=None):
        """
        Creates a new test run.
        :param project_id:The ID of the project the test run should be added to
        :param suite_id:The ID of the test suite for the test run
        (optional if the project is operating in single suite mode,
        required otherwise)
        :param name:The name of the test run
        :param description:The description of the test run
        :param milestone_id:The ID of the milestone to link to the test run
        :param assignedto_id:The ID of the user the test run should be assigned to
        :param include_all:True for including all test cases of the test suite
        and false for a custom case selection
        :param case_ids:An array of case IDs for the custom case selection
        """
        param = dict(suite_id=suite_id, name=name,
                     description=description, milestone_id=milestone_id,
                     assignedto_id=assignedto_id,
                     include_all=include_all, case_ids=case_ids)
        return self._post('add_run/{}'.format(project_id),
                          json=param)

    def update(self, run_id, name=None, assignedto_id=None,
               description=None, milestone_id=None,
               include_all=True, case_ids=None):
        """
        Updates an existing test run
        (partial updates are supported,
        i.e. you can submit and update specific fields only).
        :param run_id:The ID of the test run
        :param name:The name of the test run
        :param description:The description of the test run
        :param milestone_id:The ID of the milestone to link to the test run
        :param assignedto_id:The ID of the user the test run should be assigned to
        :param include_all:True for including all test cases of the test suite
        and false for a custom case selection
        :param case_ids:An array of case IDs for the custom case selection
        """
        param = dict(name=name,
                     description=description, milestone_id=milestone_id,
                     assignedto_id=assignedto_id,
                     include_all=include_all, case_ids=case_ids)
        return self._post('update_run/{}'.format(run_id),
                          json=param)

    def close(self, run_id):
        """
        Closes an existing test run and archives its tests & results.
        :param run_id:The ID of the test run
        """
        return self._post('close_run/{}'.format(run_id))

    def delete(self, run_id):
        """
        Deletes an existing test run.
        :param run_id:The ID of the test run
        """
        return self._post('delete_run/{}'.format(run_id))
