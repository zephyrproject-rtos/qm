#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class User(TestRailAPIBase):
    """
    Use the following API methods to request details about users.
    """
    def __repr__(self):
        return '<TestRailAPI user>'

    def get(self, user_id):
        """
        Returns an existing user.
        :param user_id:The ID of the user
        """
        return self._get('get_user/{}'.format(user_id))

    def by_email(self, email):
        """
        Returns an existing user by his/her email address.
        :param email:The email address to get the user for
        """
        return self._get('get_user_by_email&email={}'.format(email))

    def all(self):
        """
        Returns a list of users.
        """
        return self._get('get_users')
