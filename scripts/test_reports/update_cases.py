#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import glob
from pprint import pprint
sys.path.append(".")
from testrail_client import TestRailClient

from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error
import re
import datetime
import csv
from pprint import  pprint

client = TestRailClient(
        'https://zephyrproject.testrail.io',
        '<email>',
        '<token>')

def find_section(sections, section , subsection):
    found = None
    parent = None
    for s in sections:
        if s['name'] == subsection:
            found = s
        if s['name'] == section:
            parent = s

    if found and parent:
        if found['parent_id'] == parent['id']:
            return found['id']
        else:
            print(found)
            print(parent)
            return None

    print(found)
    print(parent)
    return None

def find_case_by_ref(suite, ref):
    for c in suite:
        if c['refs'] == ref:
            return c['id']
    return None

suite = client.case.for_project(5, 23)
sections = client.section.for_suite(5, suite_id=23)


with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        #print("Checking for {}".format(row[2]))
        if not find_case_by_ref(suite, row[2]):
            print("=> Case {} does not exist".format(row[2]))
            sec_id = find_section(sections, row[0], row[1])
            if sec_id:
                client.case.add(sec_id, row[2], 4 , 7, 2, None, None, row[2])
                pass
            else:
                print("    no suitable section found {}/{}".format(row[0], row[1]))


