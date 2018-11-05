#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class MileStone(TestRailAPIBase):
    """
    Use the following API methods to request details
    about milestones and to create or modify milestones.
    """
    def __repr__(self):
        return '<TestRailAPI milestone>'

    def get(self, milestone_id):
        """
        Returns an existing milestone.
        :param milestone_id:The ID of the milestone
        """
        return self._get('get_milestone/{}'.format(milestone_id))

    def for_project(self, project_id, is_completed):
        """
        Returns the list of milestones for a project.
        :param project_id:The ID of the project
        :param is_completed:1 to return completed milestones only.
        0 to return active milestones only.
        """
        if is_completed not in [0, 1]:
            raise ValueError('is_completed should be 0 or 1')
        return self._get('get_milestones/{project_id}'
                         '&is_completed={is_completed}'
                         .format(**locals()))

    def add(self, project_id, name, due_on='', description=''):
        """
        Creates a new milestone.
        :param project_id: The ID of the project the milestone should be added to
        :param name:The name of the milestone (required)
        :param due_on:The description of the milestone
        :param description: The due date of the milestone (as UNIX timestamp)
        """
        param = dict(name=name, due_on=due_on, description=description)
        return self._post('add_milestone/{}'.format(project_id),
                          json=param)

    def update(self, milestone_id, is_completed,
               name, due_on='', description=''):
        """
        Updates an existing milestone (partial updates are supported,
        i.e. you can submit and update specific fields only).
        :param milestone_id: The ID of the milestone
        :param is_completed: Specifies whether a milestone is considered completed or not
        :param name:The name of the milestone (required)
        :param due_on:The description of the milestone
        :param description: The due date of the milestone (as UNIX timestamp)
        """
        param = dict(is_completed=is_completed,name=name,
                     due_on=due_on, description=description)
        return self._post('update_milestone/{}'.format(milestone_id),
                          json=param)

    def delete(self, milestone_id):
        """
        Deletes an existing milestone.
        :param milestone_id:The ID of the milestone
        """
        return self._post('delete_milestone/{}'.format(milestone_id))
