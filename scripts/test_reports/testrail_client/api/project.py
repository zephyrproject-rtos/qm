#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class Project(TestRailAPIBase):
    """
    Use the following API methods to request details
    about projects and to create or modify projects.
    """
    def __repr__(self):
        return '<TestRailAPI project>'

    def get(self, project_id):
        """
        Returns an existing project.
        :param project_id:The ID of the project
        """
        return self._get('get_project/{}'.format(project_id))

    def all(self, is_completed=0):
        """
        Returns the list of available projects.
        :param is_completed:1 to return completed projects only.
        0 to return active projects only.
        """
        return self._get('get_projects&is_completed={}'
                         .format(is_completed))

    def add(self, name, announcement='',
            show_announcement=True,
            suite_mode=1):
        """
        Creates a new project (admin status required).
        :param name:The name of the project (required)
        :param announcement:The description of the project
        :param show_announcement:True if the announcement should be displayed
        on the project's overview page and false otherwise
        :param suite_mode:The suite mode of the project (1 for single suite mode,
        2 for single suite + baselines,
        3 for multiple suites) (added with TestRail 4.0)
        """
        param = dict(name, announcement=announcement,
                     show_announcement=show_announcement,
                     suite_mode=suite_mode)
        return self._post('add_project', json=param)

    def update(self, project_id, is_completed=True,
               name='', announcement='',
               show_announcement=True,
               suite_mode=1):
        """
        Updates an existing project
        (admin status required; partial updates are supported,
        i.e. you can submit and update specific fields only).
        :param project_id:The ID of the project
        :param is_completed:Specifies whether a project is considered completed or not
        :param name:The name of the project (required)
        :param announcement:The description of the project
        :param show_announcement:True if the announcement should be displayed
        on the project's overview page and false otherwise
        :param suite_mode:The suite mode of the project (1 for single suite mode,
        2 for single suite + baselines,
        3 for multiple suites) (added with TestRail 4.0)
        """
        param = dict(name, announcement=announcement,
                     show_announcement=show_announcement,
                     suite_mode=suite_mode,
                     is_completed=is_completed)
        return self._post('update_project/{}'.format(project_id),
                          json=param)

    def delete(self, project_id):
        """
        Deletes an existing project (admin status required).
        :param project_id:The ID of the project
        """
        return self._post('delete_project/{}'.format(project_id))
