#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class Result(TestRailAPIBase):
    """
    Use the following API methods to request details
    about test results and to add new test results.
    """
    def __repr__(self):
        return '<TestRailAPI result>'

    def get(self, test_id, **filters):
        """
        Returns a list of test results for a test.
        :param test_id:The ID of the test
        :param filters: dict, request filter
        """
        return self._get('get_results/{}'.format(test_id),
                         params=filters)

    def for_case(self, run_id, case_id, **filters):
        """
        Returns a list of test results for a test run and case combination.
        :param run_id:The ID of the test run
        :param case_id:The ID of the test case
        :param filters: dict, request filter
        """
        return self._get('get_results_for_case/{run_id}/{case_id}'
                         .format(run_id=run_id,
                                 case_id=case_id),
                         params=filters
                         )

    def for_run(self, run_id, **filters):
        """
        Returns a list of test results for a test run.
        :param run_id:The ID of the test run
        :param filters: dict, request filter
        """
        return self._get('get_results_for_run/{}'.format(run_id),
                         params=filters)

    def add(self, test_id, status_id=None, comment=None,
            vesion=None, elapsed=None, defects=None,
            assignedto_id=None, **kwargs):
        """
        Adds a new test result, comment or assigns a test.
        It's recommended to use add_results instead
        if you plan to add results for multiple tests.
        :param test_id:The ID of the test the result should be added to
        :param status_id:The ID of the test status.
        :param comment:The comment / description for the test result
        :param vesion:The version or build you tested against
        :param elapsed:The time it took to execute the test, e.g. "30s" or "1m 45s"
        :param defects:A comma-separated list of defects to link to the test result
        :param assignedto_id:The ID of a user the test should be assigned to
        """
        param = dict(status_id=status_id, comment=comment,
                     vesion=vesion, elapsed=elapsed, defects=defects,
                     assignedto_id=assignedto_id)
        param.update(**kwargs)
        return self._post('add_result/{}'.format(test_id),
                          json=param)

    def add_for_case(self, run_id, case_id, status_id=None,
                     comment=None, vesion=None, elapsed=None,
                     defects=None, assignedto_id=None, **kwargs):
        """
        Adds a new test result, comment or assigns a test
        (for a test run and case combination).
        :param run_id:The ID of the test run
        :param case_id:The ID of the test case
        :param status_id:The ID of the test status.
        :param comment:The comment / description for the test result
        :param vesion:The version or build you tested against
        :param elapsed:The time it took to execute the test, e.g. "30s" or "1m 45s"
        :param defects:A comma-separated list of defects to link to the test result
        :param assignedto_id:The ID of a user the test should be assigned to
        """
        param = dict(status_id=status_id, comment=comment,
                     vesion=vesion, elapsed=elapsed, defects=defects,
                     assignedto_id=assignedto_id)
        param.update(**kwargs)
        return self._post('add_result_for_case/{run_id}/{case_id}'
                          .format(run_id=run_id, case_id=case_id),
                          json=param)

    def add_for_cases(self, run_id, results):
        """
        Adds one or more new test results, comments or assigns one or more tests (using the case IDs).
        Ideal for test automation to bulk-add multiple test results in one step.
        :param run_id:The ID of the test run.
        :param results: results to add.
        """
        param = dict(results=results)
        res = self._post('add_results_for_cases/{}'.format(run_id),
                         json=param)
        return res

    def add_multiple(self, run_id, results):
        """
        Adds one or more new test results, comments or assigns one or more tests.
        Ideal for test automation to bulk-add multiple test results in one step.
        :param run_id:The ID of the test run.
        :param results: results to add.
        """
        param = dict(results=results)
        return self._post('add_results/{}'.format(run_id),
                          json=param)

    def field(self):
        """
        Returns a list of available test result custom fields.
        """
        return self._get('get_result_fields')
