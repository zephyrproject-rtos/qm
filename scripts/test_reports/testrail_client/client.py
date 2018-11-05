#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api import TestRailAPI


class TestRailClient(TestRailAPI):

    def __init__(self, base_url, user_name, password):
        self.user_name = user_name
        self.password = password
        if not base_url.startswith('https://'):
            base_url = 'https://' + base_url
        if not base_url.endswith('/'):
            base_url += '/'
        self.__url = base_url + 'index.php?/api/v2/'
        super(TestRailClient, self).__init__(
            self.__url, user_name, password
        )

    def __repr__(self):
        return '<TestRailClient>'

    @property
    def test_rail_url(self):
        return self.__url
