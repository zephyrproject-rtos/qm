#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase
from collections import namedtuple
import json

class Plan(TestRailAPIBase):
    """
    Use the following API methods to request details
    about test plans and to create or modify test plans.
    """
    def __repr__(self):
        return '<TestRailAPI plan>'

    def get(self, plan_id):
        """
        Returns an existing test plan.
        :param plan_id:The ID of the test plan
        """
        return self._get('get_plan/{}'.format(plan_id))

    def for_project(self, project_id, **filters):
        """
        Returns a list of test plans for a project.
        :param project_id:The ID of the project
        :param filters: dict, request filters
        """
        return self._get('get_plans/{}'.format(project_id),
                         params=filters)

    def add(self, project_id, name='', description='',
            milestone_id=None, entries=list()):
        """
        Creates a new test plan.
        :param project_id:The ID of the project the test plan should be added to
        :param name:The name of the test plan (required)
        :param description:The description of the test plan
        :param milestone_id:The ID of the milestone to link to the test plan
        :param entries:An array of objects describing the test runs of the plan
        """
        param = dict(name=name, description=description,
                     milestone_id=milestone_id, entries=entries)
        return self._post('add_plan/{}'.format(project_id),
                          json=param)

    def add_entry(self, plan_id, suite_id, name='', description='',
                  assignedto_id=None, include_all=True, case_ids=list(),
                  config_ids=list(), runs=list()):
        """
        Adds one or more new test runs to a test plan.
        :param plan_id:The ID of the plan the test runs should be added to
        :param suite_id:The ID of the test suite for the test run(s) (required)
        :param name:The name of the test run(s)
        :param description:The description of the test run(s) (requires TestRail 5.2 or later)
        :param assignedto_id:The ID of the user the test run(s) should be assigned to
        :param include_all:True for including all test cases of the test suite
        and false for a custom case selection
        :param case_ids:An array of case IDs for the custom case selection
        :param config_ids:An array of configuration IDs used for the test runs
        of the test plan entry (requires TestRail 3.1 or later)
        :param runs:An array of test runs with configurations,
        please see the example below for details (requires TestRail 3.1 or later)
        """
        param = dict(suite_id=suite_id, name=name, description=description,
                     assignedto_id=assignedto_id, include_all=include_all, case_ids=case_ids,
                     config_ids=config_ids, runs=runs)
        return self._post('add_plan_entry/{}'.format(plan_id),
                          json=param)

    def update(self, plan_id, name='', description='',
               milestone_id=None, entries=list()):
        """
        Updates an existing test plan (partial updates are supported,
        i.e. you can submit and update specific fields only).
        :param plan_id:The ID of the test plan
        :param name:The name of the test plan (required)
        :param description:The description of the test plan
        :param milestone_id:The ID of the milestone to link to the test plan
        :param entries:An array of objects describing the test runs of the plan
        """
        param = dict(name=name, description=description,
                     milestone_id=milestone_id, entries=entries)
        return self._post('update_plan/{}', format(plan_id),
                          json=param)

    def update_entry(self, plan_id, entry_id, name='',
                     description=None, assignedto_id=None,
                     include_all=True, case_ids=list()):
        """
        Updates one or more existing test runs in a plan
        (partial updates are supported, i.e. you can submit and update specific fields only).
        :param plan_id: The ID of the test plan
        :param entry_id:The ID of the test plan entry (note: not the test run ID)
        :param name:The name of the test run(s)
        :param description:The description of the test run(s)
        (requires TestRail 5.2 or later)
        :param assignedto_id:The ID of the user the test run(s) should be assigned to
        :param include_all:True for including all test cases of the test suite
        and false for a custom case selection
        :param case_ids:An array of case IDs for the custom case selection
        """
        return self._post('update_plan_entry/{plan_id}/{entry_id}'
                          .format(plan_id=plan_id, entry_id=entry_id),
                          json=dict(name=name, description=description,
                                    assignedto_id=assignedto_id,
                                    include_all=include_all, case_ids=case_ids)
                          )

    def close(self, plan_id):
        """
        Closes an existing test plan and archives its test runs & results.
        :param plan_id:The ID of the test plan
        """
        return self._post('close_plan/{}'.format(plan_id))

    def delete(self, plan_id):
        """
        Deletes an existing test plan.
        :param plan_id:The ID of the test plan
        """
        return self._post('delete_plan/{}'.format(plan_id))

    def delete_entry(self, plan_id, entry_id):
        """
        Deletes one or more existing test runs from a plan.
        :param plan_id:The ID of the test plan
        :param entry_id:The ID of the test plan entry (note: not the test run ID)
        """
        return self._post('delete_plan_entry/{plan_id}/{entry_id}'
                          .format(plan_id=plan_id,
                                  entry_id=entry_id)
                          )
