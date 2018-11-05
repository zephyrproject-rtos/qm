#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class Test(TestRailAPIBase):
    """
    Use the following API methods to request details about tests.
    """
    def __repr__(self):
        return '<TestRailAPI test>'

    def get(self, test_id):
        """
        Returns an existing test.
        :param test_id: The ID of the test
        """
        return self._get('get_test/{}'.format(test_id))

    def for_run(self, run_id, **filters):
        """
        Returns a list of tests for a test run.
        :param run_id:The ID of the test run
        :param filters: dict, request filter
        """
        return self._get('get_tests/{}'.format(run_id),
                         params=filters)
