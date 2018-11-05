#!/usr/bin/env python
# -*- coding: utf-8 -*-


from testrail_client.api.base import TestRailAPIBase


class Case(TestRailAPIBase):
    """
    Use the following API methods to request details
    about test cases and to create or modify test cases.
    """
    def __repr__(self):
        return '<TestRailAPI Case>'

    def get(self, case_id):
        """
        Returns an existing test case.

        :param case_id: The ID of the test case
        """
        return self._get('get_case/{}'.format(case_id))

    def for_project(self, project_id, suite_id='', section_id='', **filters):
        """
        Returns a list of test cases for a test suite or specific section in a test suite.

        :param project_id: The ID of the project
        :param suite_id: The ID of the test suite (optional
        if the project is operating in single suite mode)
        :param section_id: The ID of the section (optional)
        :param filters: dict, requests filter support fields
        """
        return self._get('get_cases/{project_id}'
                         '&suite_id={suite_id}'
                         '&section_id={section_id}'.format(**locals()),
                         params=filters)

    def add(self, section_id, title, template_id=1,
            type_id=1, priority_id=3, estimate=None, milestone_id=None,
            refs=None, custom_steps=list(), preconditions='', **kwargs):
        """
        Creates a new test case.

        :param section_id: The ID of the section the test case should be added to
        :param title: str, The title of the test case (required)
        :param template_id: int, The ID of the template (field layout)
        (requires TestRail 5.2 or later)
        :param type_id: int, The ID of the case type
        :param priority_id: int, The ID of the case priority
        :param estimate: str, The estimate, e.g. "30s" or "1m 45s"
        :param milestone_id: int, The ID of the milestone to link to the test case
        :param refs: str, A comma-separated list of references/requirements
        :param custom_steps
        """
        param = dict(title=title, template_id=template_id,
                     type_id=type_id, priority_id=priority_id,
                     estimate=estimate, milestone_id=milestone_id,
                     refs=refs, custom_steps=custom_steps, custom_preconds= preconditions)
        param.update(**kwargs)
        return self._post('add_case/{}'.format(section_id),
                          json=param)

    def update(self, case_id, title, template_id=1,
               type_id=1, priority_id=3, estimate=None, milestone_id=None,
               refs=None, custom_steps=list(), **kwargs):
        """
        Updates an existing test case (partial updates are supported,
        i.e. you can submit and update specific fields only).

        :param case_id: The ID of the test case
        :param title: str, The title of the test case (required)
        :param template_id: int, The ID of the template (field layout)
        (requires TestRail 5.2 or later)
        :param type_id: int, The ID of the case type
        :param priority_id: int, The ID of the case priority
        :param estimate: str, The estimate, e.g. "30s" or "1m 45s"
        :param milestone_id: int, The ID of the milestone to link to the test case
        :param refs: str, A comma-separated list of references/requirements
        """
        param = dict(title=title, template_id=template_id,
                     type_id=type_id, priority_id=priority_id,
                     estimate=estimate, milestone_id=milestone_id,
                     refs=refs, custom_steps=custom_steps)
        param.update(**kwargs)
        return self._post('update_case/{}'.format(case_id),
                          json=param)

    def delete(self, case_id):
        """
        Deletes an existing test case.

        :param case_id: The ID of the test case
        """
        return self._post('delete_case/{}'.format(case_id))

    def custom_fields(self):
        """
        Returns a list of available test case custom fields.
        """
        return self._get('get_case_fields')

    def types(self):
        """
        Returns a list of available case types.
        """
        return self._get('get_case_types')

    def status(self):
        """
        Use the following API methods to request details about test statuses.
        """
        return self._get('get_statuses')
