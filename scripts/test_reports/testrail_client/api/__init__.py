#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testrail_client.api.case import Case
from testrail_client.api.configurations import Config
from testrail_client.api.milestone import MileStone
from testrail_client.api.plan import Plan
from testrail_client.api.project import Project
from testrail_client.api.result import Result
from testrail_client.api.run import Run
from testrail_client.api.section import Section
from testrail_client.api.statuses import Statuses
from testrail_client.api.suite import Suite
from testrail_client.api.test import Test
from testrail_client.api.user import User


class TestRailAPI(object):
    __version__ = 'v2'

    def __init__(self, url, user_name, password):
        self.url = url
        self.user_name = user_name
        self.password = password

    def __repr__(self):
        return '<TestRail API>'

    @property
    def user(self):
        return User(self.url, self.user_name, self.password)

    @property
    def case(self):
        return Case(self.url, self.user_name, self.password)

    @property
    def config(self):
        return Config(self.url, self.user_name, self.password)

    @property
    def milestone(self):
        return MileStone(self.url, self.user_name, self.password)

    @property
    def plan(self):
        return Plan(self.url, self.user_name, self.password)

    @property
    def project(self):
        return Project(self.url, self.user_name, self.password)

    @property
    def result(self):
        return Result(self.url, self.user_name, self.password)

    @property
    def run(self):
        return Run(self.url, self.user_name, self.password)

    @property
    def section(self):
        return Section(self.url, self.user_name, self.password)

    @property
    def statuses(self):
        return Statuses(self.url, self.user_name, self.password)

    @property
    def suite(self):
        return Suite(self.url, self.user_name, self.password)

    @property
    def test(self):
        return Test(self.url, self.user_name, self.password)
