#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class Suite(TestRailAPIBase):
    """
    Use the following API methods to request details
    about test suites and to create or modify test suites.
    """
    def __repr__(self):
        return '<TestRailAPI suite>'

    def get(self, suite_id):
        """
        Returns an existing test suite.
        :param suite_id:The ID of the test suite
        """
        return self._get('get_suite/{}'.format(suite_id))

    def for_project(self, project_id):
        """
        Returns a list of test suites for a project.
        :param project_id:The ID of the project
        """
        return self._get('get_suites/{}'.format(project_id))

    def add(self, project_id, name, description=None):
        """
        Creates a new test suite.
        :param project_id:The ID of the project the test suite should be added to
        :param name:The name of the test suite (required)
        :param description:The description of the test suite
        """
        param = dict(name=name, description=description)
        return self._post('add_suite/{}'.format(project_id),
                          json=param)

    def update(self, suite_id, name, description=None):
        """
        Creates a new test suite.
        :param suite_id:The ID of the test suite
        :param name:The name of the test suite (required)
        :param description:The description of the test suite
        """
        param = dict(name=name, description=description)
        return self._post('add_suite/{}'.format(suite_id),
                          json=param)

    def delete(self, suite_id):
        """
        Deletes an existing test suite.
        :param suite_id:The ID of the test suite
        """
        return self._post('delete_suite/{}'.format(suite_id))
