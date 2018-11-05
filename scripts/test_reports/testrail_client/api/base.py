#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
from testrail_client.api.error import TesRailAPIError, TestRailAuthError


# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.NOTSET)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.NOTSET)
requests_log.propagate = True

def check_execption(func):
    def _check(*arg, **kws):
        resp = func(*arg, **kws)
        if resp.status_code >= 400:
            if resp.status_code == 403:
                raise TestRailAuthError(403, 'No permission')
            elif resp.status_code == 401:
                raise TestRailAuthError(401, 'Not authorized')
            else:
                raise TesRailAPIError(resp)
        try:
            return resp.json()
        except Exception:
            return resp.content
    return _check


def format_request_filter(func):
    def _format(*args, **kwargs):
        params = kwargs.get('params', dict())
        for key in params:
            if isinstance(params[key], list):
                params[key] = ','.join(map(str, params[key]))
        return func(*args, **kwargs)
    return _format


class TestRailAPIBase(object):

    def __init__(self, url, user_name, password):
        self.url = url
        self.user_name = user_name
        self.password = password
        self.header = {
            'Content-Type': 'application/json'
        }

    def __repr__(self):
        return '<TestRailAPI Base>'

    @format_request_filter
    @check_execption
    def _get(self, url, **opts):
        return requests.get(self.url + url,
                            auth=(self.user_name, self.password),
                            headers=self.header,
                            **opts)

    @check_execption
    def _post(self, url, **opts):
        return requests.post(self.url + url,
                             auth=(self.user_name, self.password),
                             headers=self.header,
                             **opts)
