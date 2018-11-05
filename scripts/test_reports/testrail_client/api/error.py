#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TestRailBaseError(Exception):
    def __str__(self):
        return "[TestRailAPI] %s || (%s) || %s" \
               % (self.status, self.reason, self.msg)


class TestRailAuthError(TestRailBaseError):
    def __init__(self, status_code, reason):
        self.status = status_code
        self.reason = reason
        self.msg = dict()


class TesRailAPIError(TestRailBaseError):
    def __init__(self, res):
        self.status = res.status_code
        self.reason = res.reason
        self.msg = res.content
