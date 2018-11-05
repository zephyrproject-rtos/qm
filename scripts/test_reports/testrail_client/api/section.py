#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class Section(TestRailAPIBase):
    """
    Use the following API methods to request details
    about sections and to create or modify sections.
    Sections are used to group and organize test cases in test suites.
    """
    def __repr__(self):
        return '<TestRailAPI section>'

    def get(self, section_id):
        """
        Returns an existing section.
        :param section_id: The ID of the section
        """
        return self._get('get_section/{}'.format(section_id))

    def for_suite(self, project_id, suite_id=''):
        """
        Returns a list of sections for a project and test suite.
        :param project_id:The ID of the project
        :param suite_id:The ID of the test suite
        (optional if the project is operating in single suite mode)
        """
        return self._get('get_sections/{project_id}&suite_id={suite_id}'
                         .format(**locals()))

    def add(self, project_id, description=None, suite_id=None,
            parent_id=None, name=None):
        """
        Creates a new section.
        :param project_id:The ID of the project
        :param description:The description of the section
        (added with TestRail 4.0)
        :param suite_id:The ID of the test suite
        (ignored if the project is operating in single suite mode,
        required otherwise)
        :param parent_id:The ID of the parent section
        (to build section hierarchies)
        :param name:The name of the section (required)
        """
        param = dict(description=description, suite_id=suite_id,
                     parent_id=parent_id, name=name)
        return self._post('add_section/{}'.format(project_id),
                          json=param)

    def update(self, section_id, description=None, suite_id=None,
               parent_id=None, name=None):
        """
        Creates a new section.
        :param section_id:The ID of the section
        :param description:The description of the section
        (added with TestRail 4.0)
        :param name:The name of the section (required)
        """
        param = dict(description=description, suite_id=suite_id,
                     parent_id=parent_id, name=name)
        return self._post('update_section/{}'.format(section_id),
                          json=param)

    def delete(self, section_id):
        """
        Deletes an existing section.
        :param section_id:The ID of the section
        """
        return self._post('delete_section/{}'.format(section_id))
