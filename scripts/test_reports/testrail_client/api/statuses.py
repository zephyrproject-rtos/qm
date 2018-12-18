#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.base import TestRailAPIBase


class Statuses(TestRailAPIBase):
    """
    Use the following API methods to request details about tests.
    """
    def __repr__(self):
        return '<TestRailAPI statuses>'

    def get(self):
        """
        Returns all statuses.
        """
        return self._get('get_statuses')

