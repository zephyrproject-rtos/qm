#!/usr/bin/env python
# -*- coding: utf-8 -*-


from testrail_client.api.base import TestRailAPIBase


class Config(TestRailAPIBase):
    """
    Use the following API methods to request details
    about configurations and to create or modify configurations.
    """
    def __repr__(self):
        return '<TestRailAPI config>'

    def get(self, project_id):
        """
        Returns a list of available configurations,
        grouped by configuration groups (requires TestRail 3.1 or later).

        :param project_id: The ID of the project
        """
        return self._get('get_configs/{}'.format(project_id))

    def add(self, config_group_id, name=''):
        """
        Creates a new configuration (requires TestRail 5.2 or later).

        :param config_group_id: The ID of the configuration group
        the configuration should be added to
        :param name: str, The name of the configuration (required)
        """
        return self._post('add_config/{}'.format(config_group_id),
                          json=dict(name=name))

    def update(self, config_group_id, name=''):
        """
        Updates an existing configuration (requires TestRail 5.2 or later).

        :param config_group_id: The ID of the configuration group
        the configuration should be added to
        :param name: str, The name of the configuration (required)
        """
        return self._post('update_config/{}'.format(config_group_id),
                          json=dict(name=name))

    def delete(self, config_id):
        """
        Deletes an existing configuration (requires TestRail 5.2 or later).

        :param config_id:
        """
        return self._post('delete_config/{}'.format(config_id))

    def add_group(self, project_id, name=''):
        """
        Creates a new configuration group (requires TestRail 5.2 or later).
        :param project_id: The ID of the project the configuration group should be added to
        :param name: The name of the configuration group (required)
        """
        return self._post('add_config_group/{}'.format(project_id),
                          json=dict(name=name))

    def update_group(self, config_group_id, name):
        """
        Updates an existing configuration group (requires TestRail 5.2 or later).
        :param config_group_id: The ID of the configuration group
        :param name: The name of the configuration group
        """
        return self._post('update_config_group/{}'.format(config_group_id),
                          json=dict(name=name))

    def delete_group(self, config_group_id):
        """
        Deletes an existing configuration (requires TestRail 5.2 or later).
        :param config_group_id: The ID of the configuration
        """
        return self._post('delete_config_group/{}'.format(config_group_id))

    def priority(self):
        """
        Returns a list of available priorities.
        """
        return self._get('get_priorities')

    def template(self, project_id):
        """
        Returns a list of available templates (requires TestRail 5.2 or later).
        :param project_id:The ID of the project
        """
        return self._get('get_templates/{}'.format(project_id))
