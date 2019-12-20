#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Intel Corporation
#
# SPDX-License-Identifier: Apache-2.0

# Script to upload results to testrail.

import sys
import os
import glob
from pprint import pprint
sys.path.append(".")
from testrail_client import TestRailClient

from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error
import re
import datetime
import argparse
import configparser

retest_text = "description: subtestcase didn't run: likely the image failed to build or to deploy"

DEBUG = False

err_messages = []
upl_messages = []
files_counter = 0
files_error = 0
sections = []

def debug(msg):
    if DEBUG:
        print(msg)

class TestRail():

    def __init__(self):
        self.client = None

    def authorize(self):
        self.project = 'https://zephyrproject.testrail.io'
        self.user = os.environ.get('TESTRAIL_USER', None)
        self.token = os.environ.get('TESTRAIL_TOKEN', None)

        self.client = TestRailClient(self.project, self.user, self.token)


class Config():
    def __init__(self, name, group, id):
        self.name = name
        self.group_id = group
        self.id = id


class Configurations(TestRail):

    def __init__(self, project_id):
        super().authorize()
        self.project = project_id
        self.group_id = None
        self.configs = []

    def get(self, group):
        configs = self.client.config.get(self.project)

        # search for group
        idx = next((index for (index, d) in enumerate(configs) if d["name"] == group), None)
        if configs and idx is not None and idx >= 0:
            self.group_id = configs[idx]['id']
            debug(self.group_id)
            for c in configs[idx]['configs']:
                p = Config(c['name'], c['group_id'], c['id'])
                self.configs.append(p)
        else:
            print("Creating new group")
            ret = self.client.config.add_group(project_id=self.project, name=group)
            self.group_id = ret.get("id")
    def add(self, config):
        self.client.config.add(self.group_id, config)

    def provides(self, config):
        for p in self.configs:
            if p.name == config:
                return p.id

        return 0


class Status(TestRail):

    def __init__(self, project_id):

        super().authorize()

        self.PASSED = None
        self.FAILED = None
        self.BLOCKED = None
        self.SKIPPED = None
        self.RETEST = None
        self.UNTESTED = None
        self.UNGRADED = None
        self.TIMEOUT = None
        self.ERROR = None

        self.populate()

    def populate(self):
        statuses = self.client.case.status()

        for s in statuses:
            sid = s["id"]
            sname = s['name']

            if sname == "passed":
                self.PASSED = sid
            elif sname == "failed":
                self.FAILED = sid
            elif sname == "blocked":
                self.BLOCKED = sid
            elif sname == "skipped":
                self.SKIPPED = sid
            elif sname == "untested":
                self.UNTESTED = sid
            elif sname == "ungraded":
                self.UNGRADED = sid
            elif sname == "timeout":
                self.TIMEOUT = sid
            elif sname == "error":
                self.ERROR = sid
            elif sname == "retest":
                self.RETEST = sid


class TestRun(TestRail):

    def __init__(self):
        super().authorize()

        self.config_ids = []
        self.runs = []

        self.milestone = None
        self.variants = []
        self.result_files = []
        self.project_id = None
        self.version = None
        self.suite = None
        self.plan = None
        self.result_files = []
        self.status = None
        self.cases = []
        self.final_results = []
        self.plan_entries = None
        self.title = "Test Run"
        self.configbuginfo = None

    def configure(self):
        self.status = Status(self.project_id)
        self.cases = self.client.case.for_project(project_id=self.project_id, suite_id=self.suite)

        if not self.plan:
            today = datetime.date.today().strftime("%B %d, %Y")
            self.plan = self.client.plan.add(self.project_id,
                                             "{}: {} {}".format(self.title, self.version, today),
                                             milestone_id=self.milestone)

    def get_case_id(self, reference):
        for case in self.cases:
            if case['refs'] == reference:
                return case['id']
        return 0

    def get_case_name(self, name):
        return name

    def get_case_text(self, text):
        return text


    def parse_buginfofile(self, buginfos_file):
        try:
            if os.path.isfile(buginfos_file):
                self.configbuginfo = configparser.ConfigParser()
                self.configbuginfo.read(buginfos_file)

            else:
                err_msg = "ERROR5: The file is not exist for bug information: {}".format(buginfos_file)
                err_messages.append(err_msg)

        except:
            self.configbuginfo = None
            err_msg = "ERROR5: Can't parse bug info file {}".format(buginfos_file)
            err_messages.append(err_msg)


    def parse_files(self):
        for result_file in self.result_files:
            self.parse_file(result_file)

    def find_case_by_ref(suite, ref):
        for c in suite:
            if c['refs'] == ref:
                return c['id']
        return None

    def parse_file(self, result_file):

        passed_counter = 0
        skipped_counter = 0
        failure_counter = 0
        config = result_file.get('config')

        try:
            junit_xml = JUnitXml.fromfile(result_file['file'])
            print("\nParsing file success {}".format(result_file['file']))

            results_to_upload = []
            parents = {}

            for suite in junit_xml:
                for testcase in suite:
                    if testcase.result and testcase.result.type == 'skipped':
                        continue

                    ref = self.get_case_name(testcase.name)

                    if  testcase.result:
                        tc = testcase
                    elif testcase.name in parents:
                        tc = parents[testcase.name]
                    else:
                        parent = self.find_parent_in_junit(junit_xml, testcase.name)
                        if parent:
                            debug("--> found parent failure: %s -> %s" %(parent.name, parent.result))

                            runid_err = "eval error: expected console output 'RunID"
                            runid_result = "console output: RunID"

                            if parent.result._elem.text and runid_err in parent.result._elem.text and runid_result in parent.result._elem.text:

                                debug("{} parent is FALSE NEGATIVE, so keep sub-test result".format(testcase.name))
                                tc = testcase
                            else:
                                tc = parent

                            parents[testcase.name] = parent
                        else:
                            tc = testcase

                    cr = {}
                    cr['ref'] = ref

                    filtered = ""
                    infra_issue = False
                    if tc.result:
                        override = None

                        text = tc.result._elem.text
                        if text:
                            filtered = self.get_case_text(text)

                        if override:
                            test_status = override
                        else:
                            if tc.result.type == 'error' and tc.result.message == 'Infrastructure':
                                test_status = self.status.RETEST
                                infra_issue = True
                            elif tc.result.type == 'error':
                                test_status = self.status.BLOCKED
                                if self.configbuginfo and self.configbuginfo.has_section(config) and self.configbuginfo.has_option(config, ref):
                                    cr['defects'] = self.configbuginfo.get(config, ref)
                            elif tc.result.type == 'skipped':
                                test_status = self.status.SKIPPED
                                skipped_counter += 1
                            elif tc.result.type == 'failure':
                                test_status = self.status.FAILED
                                failure_counter += 1
                                if self.configbuginfo and self.configbuginfo.has_section(config) and self.configbuginfo.has_option(config, ref):
                                    cr['defects'] = self.configbuginfo.get(config, ref)
                            else:
                                test_status = self.status.RETEST

                            status_text = tc.result.type

                        cr['status_id'] = test_status
                    else:
                        cr['status_id'] = self.status.PASSED
                        status_text = 'passed'
                        passed_counter += 1

                    debug("{}: {} => {}".format(config, testcase.name, status_text))
                    if filtered == "" and infra_issue:
                        cr['comment'] = "Infrastructure issue, please retest."
                    else:
                        cr['comment'] = filtered

                    cr['version'] = self.version
                    results_to_upload.append(cr)

                print("Passed counter: ", passed_counter)
                print("Skipped counter: ", skipped_counter)
                print("Failure+Error counter: ", failure_counter)

            #uncomment line below, to see results to upload
            #pprint(results_to_upload)

            tmp_res = []
            tids = []
            missed_testcases = []
            missed_cases_counter = 0

            for result in results_to_upload:
                ref = result['ref']
                case_id = self.get_case_id(ref)
                if case_id:
                    tids.append(case_id)
                    result['case_id'] = case_id
                    del result['ref']
                    tmp_res.append(result)
                else:
                    missed_testcases.append(ref)
                    missed_cases_counter += 1

            if(missed_testcases):
                print("\n{} test case(s) below not found in the TestRail suite. Add missed case(s) to TestRail and run script again:".format(missed_cases_counter))
                for i in range(len(missed_testcases)):
                    print(missed_testcases[i])
                err_file_name = result_file['file']
                err_file_name = err_file_name.split("/")[1]
                err_msg ="WARNING1: TestRail doesn't contain {} test case(s) from a file {} . New case(s) must be added to TestRail manually and then run script again.".format(missed_cases_counter, err_file_name)
                err_messages.append(err_msg)

            entry = {
                "include_all": False,
                "case_ids": tids,
                "config_ids": [result_file['id']],
            }
            self.final_results.append({'config': config, 'results': tmp_res, 'run_entry': entry, 'config_id': result_file['id']})
        except:
            err_file_name = result_file['file']
            err_file_name = err_file_name.split("/")[1]
            err_msg = "ERROR1: Can't parse file {}".format(err_file_name)
            err_messages.append(err_msg)
            global files_error
            files_error += 1


    def process(self):
        if self.buginfos_file:
            self.parse_buginfofile(self.buginfos_file)
        self.parse_files()
        print('\n')
        for fr in self.final_results:
            print("Creating plan configuration for {}".format(fr.get('config')))
            self.config_ids.append(fr['config_id'])
            self.runs.append(fr['run_entry'])
        print("\n")

        self.plan_entries = self.client.plan.add_entry(self.plan['id'], self.suite, '{} Test Run {}'.format(self.title, self.version) ,
                                                         config_ids=self.config_ids, runs=self.runs)

    def upload(self):
        plan = self.client.plan.get(self.plan['id'])
        global files_error
        global files_counter

        runs = []
        for entry in plan['entries']:
            runs = entry['runs']

        for rr in self.final_results:
            match_platform = True

            for r in runs:
                if r['config'] == rr.get('config'):
                    try:
                        match_platform = False
                        self.client.result.add_for_cases(r['id'], rr.get('results'))
                        upl_msg = "Submitted results for " + format(r['config']) + " with RunID:" + format(r['id']) + " on PlanID:" + format(self.plan['id'])
                        upl_messages.append(upl_msg)
                        files_counter += 1
                    except:
                        err_msg ="ERROR2: Can't submit results for " + format(rr.get('config')) +" on PlanID:"+ format(self.plan['id'])
                        err_messages.append(err_msg)
                        files_error += 1
            if match_platform:
                err_msg = "ERROR4: In the TestRail can't find the platfrom: " + format(rr.get('config'))+" for PlanID:"+format(self.plan['id'])
                err_messages.append(err_msg)
                files_error += 1


class SanityCheckBatch(TestRun):

    def __init__(self, result_directory, project_id, version, suite, milestone, plan, buginfo_file=None):
        super().__init__()
        super().authorize()

        global version_split
        version_split = 0
        version_split = version.split("-")[4]
        if plan:
            self.plan = self.client.plan.get(plan)

            pprint(self.plan)
            self.project_id = self.plan.get('project_id', None)
        else:
            self.project_id = project_id
        self.version = version
        self.suite = suite
        self.milestone = milestone
        self.results_directory = result_directory
        self.buginfos_file = buginfo_file
        self.title = "Zephyr Daily Test"

    def get_case_name(self, name):
        return name

    def find_parent_in_junit(self, junit_xml, name):
        return None

    def get_case_text(self, text):
        return text

    def discover(self):
        for j in glob.glob("{}/*__zephyr*.xml".format(self.results_directory)):
                file = os.path.basename((j))
                file_meta = file.split("__")
                file_branch = file.split("_")[-1]
                file_branch = file_branch.split(".")
                if file_branch[0]==version_split:
                    platform = file_meta[0].replace("junit-", "")
                    self.result_files.append({"file": j, "config": platform})
                    print("File", file , "submitted")
                else:
                    err_msg = "ERROR3: File "+file+" can't be submitted. Version is not current master version"
                    err_messages.append(err_msg)
                    global files_error
                    files_error += 1

        # Get platforms from project
        p = Configurations(project_id=self.project_id)
        p.get("Platforms")

        # See if we need to create new configurations for platforms on project
        for rf in self.result_files:
            config = rf['config']
            if p.provides(config=config) == 0:
                print("Need to create new config %s" % rf.get('config'))
                p.add(config)

        # update
        p.get("Platforms")
        for rf in self.result_files:
            rf['id'] = p.provides(rf.get('config'))

    def sanitycheck_log(self):

        if len(upl_messages) != 0:
            print('\n====================Results====================')
            for j in range(len(upl_messages)):
                print(upl_messages[j])
        else:
            print("No uploaded platforms")

        print('\n====================Total summary====================')
        if (files_counter != 0):
            print(files_counter, "file(s) uploaded")
        if (files_error != 0):
            print(files_error, "file(s) not uploaded")

        print('\n====================Error messages====================')
        if len(err_messages) != 0:
                for i in range(len(err_messages)):
                        print(err_messages[i])
        else:
            print("No errors")

        print('\n====================End====================')


class SanityCheck(TestRun):

    def __init__(self, results_file, config, project_id, version, suite, milestone, plan, buginfo_file=None):
        super().__init__()
        super().authorize()

        if plan:
            self.plan = self.client.plan.get(plan)

            pprint(self.plan)
            self.project_id = self.plan.get('project_id', None)
        else:
            self.project_id = project_id

        self.config = config
        self.version = version
        self.suite = suite
        self.results_file = results_file
        self.milestone = milestone
        self.buginfos_file = buginfo_file
        self.title = "Sanitycheck"

    def get_case_name(self, name):
        return name

    def find_parent_in_junit(self, junit_xml, name):
        return None

    def get_case_text(self, text):
        return text

    def discover(self):

        self.result_files.append({"file": self.results_file, "config": self.config})

        # Get platforms from project
        p = Configurations(project_id=self.project_id)
        p.get("Platforms")

        # See if we need to create new configurations for platforms on project
        for rf in self.result_files:
            config = rf['config']
            if p.provides(config=config) == 0:
                print("Need to create new config %s" % rf.get('config'))
                p.add(config)

        # update
        p.get("Platforms")
        for rf in self.result_files:
            rf['id'] = p.provides(rf.get('config'))

    def sanitycheck_log(self):

        if len(upl_messages) != 0:
            print('\n====================Results====================')
            for j in range(len(upl_messages)):
                print(upl_messages[j])
        else:
            print("No uploaded platform")

        print('\n====================Total summary====================')
        if (files_counter != 0):
            print(files_counter, "file uploaded")
        if (files_error != 0):
            print(files_error, "file not uploaded")

        print('\n====================Error messages====================')
        if len(err_messages) != 0:
                for i in range(len(err_messages)):
                        print(err_messages[i])
        else:
            print("No errors")

        print('\n====================End====================')


class MaxwellPro(TestRun):

    def __init__(self, results_file, config, project_id, version, suite, milestone, plan):
        super().__init__()
        super().authorize()

        if plan:
            self.plan = self.client.plan.get(plan)
            self.project_id = self.plan.get('project_id', None)
        else:
            self.project_id = project_id

        self.config = config
        self.version = version
        self.suite = suite
        self.results_file = results_file
        self.milestone = milestone
        self.title = "Maxwell TCP/IP"

    def get_case_name(self, name):
        return name

    def get_case_text(self, text):
        return text

    def results_for_config(self, results_file, config):

        results = []
        with open(self.results_file, "r") as file:
            for line in file.readlines():
                #match = re.match(r"\s*(\d+)/(\d+)\s+([^\s]+)\s+(%s)\s+(PASS|SKIPPED|FAIL|UNGRADED)".format(config), line)
                match = re.match(r"\s*(\d+)/(\d+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)", line)
                if match and match.group(4) == config:
                    results.append({'id': match.group(3), 'result': match.group(5)})
        return results

    def parse_file(self, result_file):

        config = result_file.get('config')
        print("Parsing {}".format(result_file['file']))

        results = self.results_for_config(result_file.get('file'), config)
        results_to_upload = []

        for r in results:
            cr = {}
            cr['ref'] = r['id'].replace(".", "-").upper()

            result = r.get('result')

            if result == 'PASS':
                test_status = self.status.PASSED
            elif result == 'SKIPPED':
                test_status = self.status.SKIPPED
            elif result == 'FAIL':
                test_status = self.status.FAILED
            elif result == 'FAIL':
                test_status = self.status.FAILED
            elif result == 'UNGRADED':
                test_status = self.status.UNGRADED

            else:
                test_status = self.status.RETEST

            cr['status_id'] = test_status
            cr['version'] = self.version

            results_to_upload.append(cr)

        tmp_res = []
        tids = []

        for result in results_to_upload:

            ref = result.get('ref')
            case_id = self.get_case_id(ref)
            if case_id:
                tids.append(case_id)

                result['case_id'] = case_id
                del result['ref']
                tmp_res.append(result)
            else:
                print("Can't find case for {}".format(ref))

        entry = {
            "include_all": False,
            "case_ids": tids,
            "config_ids": [result_file['id']],
        }
        self.final_results.append(
            {'config': config, 'results': tmp_res, 'run_entry': entry, 'config_id': result_file['id']})

    def discover(self):

        results = {}
        with open(self.results_file, "r") as file:
            for line in file.readlines():
                match = re.match(r"\s*(\d+)/(\d+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)", line)
                if match:
                    config = match.group(4)
                    if results.get(config, None):
                        config_results = results.get(config)
                        config_results.append({'id': match.group(2), 'result': match.group(5)})
                        results[config] = config_results
                    else:
                        results[config] = [{'id': match.group(3), 'result': match.group(5)}]


        for config in results.keys():
            self.result_files.append({"file": self.results_file, "config": config})

        # Get platforms from project
        p = Configurations(project_id=self.project_id)
        p.get("Protocols")

        # See if we need to create new configurations on project
        for rf in self.result_files:
            config = rf['config']
            if p.provides(config=config) == 0:
                print("Need to create new config %s" % config)
                p.add(config)

        # update
        p.get("Protocols")
        for rf in self.result_files:
            rf['id'] = p.provides(rf.get('config'))


class AutoPTS(TestRun):

    def __init__(self, results_file, config, project_id, version, suite, milestone, plan):
        super().__init__()
        super().authorize()

        if plan:
            self.plan = self.client.plan.get(plan)
            self.project_id = self.plan.get('project_id', None)
        else:
            self.project_id = project_id

        self.config = config
        self.version = version
        self.suite = suite
        self.results_file = results_file
        self.milestone = milestone
        self.title = "Bluetooth AutoPTS"

    def get_case_name(self, name):
        return name

    def get_case_text(self, text):
        return text

    def results_for_config(self, results_file, config):

        results = []
        with open(self.results_file, "r") as file:
            for line in file.readlines():
                match = re.match(r"(.*)\t([^\s]+)\t(.*)", line)
                if match:
                    results.append({'id': match.group(2), 'result': match.group(3).strip()})
        return results

    def parse_file(self, result_file):

        config = result_file.get('config')
        print("Parsing {}".format(result_file['file']))

        results = self.results_for_config(result_file.get('file'), config)
        results_to_upload = []

        for r in results:
            cr = {}
            cr['ref'] = r['id']

            result = r.get('result')

            if result == 'PASS':
                test_status = self.status.PASSED
            elif result == 'SKIPPED':
                test_status = self.status.SKIPPED
            elif result == 'FAIL':
                test_status = self.status.FAILED
            elif result == 'INCONC':
                test_status = self.status.UNGRADED
            elif result == 'BTP ERROR':
                test_status = self.status.ERROR
            elif result in ['BTP TIMEOUT', 'PTS TIMEOUT']:
                test_status = self.status.TIMEOUT
            else:
                test_status = self.status.RETEST

            cr['status_id'] = test_status
            cr['version'] = self.version

            results_to_upload.append(cr)

        tmp_res = []
        tids = []

        for result in results_to_upload:

            ref = result.get('ref')
            case_id = self.get_case_id(ref)
            if case_id:
                tids.append(case_id)

                result['case_id'] = case_id
                del result['ref']
                tmp_res.append(result)
            else:
                print("Cant find case for {}".format(ref))

        entry = {
            "include_all": False,
            "case_ids": tids,
            "config_ids": [result_file['id']],
        }
        self.final_results.append(
            {'config': config, 'results': tmp_res, 'run_entry': entry, 'config_id': result_file['id']})

    def discover(self):

        results = {}
        self.result_files.append({"file": self.results_file, "config": self.config})

        # Get platforms from project
        p = Configurations(project_id=self.project_id)
        p.get("Platforms")

        # See if we need to create new configurations on project
        for rf in self.result_files:
            config = rf['config']
            if p.provides(config=config) == 0:
                print("Need to create new config %s" % config)
                p.add(config)

        # update
        p.get("Platforms")
        for rf in self.result_files:
            rf['id'] = p.provides(rf.get('config'))


def parse_args():
    parser = argparse.ArgumentParser(
                description="Upload test results testrail")


    parser.add_argument("--runner", default='sanitycheck', choices=['sanitycheckbatch', 'sanitycheck', 'maxwell', 'autopts'],
                        help="""
Select runner to import from.
""")

    result_file_select = parser.add_argument_group("Result files (input)",
                                        """

You can either select a directory with multiple files or just point to
one file depending on the source of the results.

SanitycheckBatch expects a directory with multiple files.
Sanitycheck expects 1 file per configuration.
                                        """)

    xor_results = result_file_select.add_mutually_exclusive_group()
    xor_results.add_argument('-j', '--results-dir', default=None,
            help="Directory with test result files")

    xor_results.add_argument('-f', '--results-file', default=None,
            help="File with test results format.")

    parser.add_argument('-b', '--buginfo-file', default=None,
            help="File with bug info format.")

    parser.add_argument('-c', '--config', default=None,
            help="Configuration name.")

    parser.add_argument('-V', '--commit', default=None,
        help="Version being tested (git desribe string)")

    parser.add_argument('-p', '--project', type=int, help="Project ID")
    parser.add_argument('-s', '--suite', type=int, help="Suite ID")

    parser.add_argument("-m", "--milestone", type=int, help="Milestone ID")
    parser.add_argument('-P', '--plan', type=int, help="Test plan ID")

    return parser.parse_args()




def main():
    args = parse_args()

    if args.runner == 'maxwell':
        tr = MaxwellPro(results_file=args.results_file,
                         config=args.config,
                         project_id=args.project,
                         suite=args.suite,
                         version=args.commit,
                         milestone=args.milestone,
                         plan=args.plan)
    elif args.runner == 'sanitycheck':
        tr = SanityCheck(results_file=args.results_file,
                         config=args.config,
                         project_id=args.project,
                         suite=args.suite,
                         version=args.commit,
                         milestone=args.milestone,
                         plan=args.plan,
                         buginfo_file=args.buginfo_file)
    elif args.runner == 'sanitycheckbatch':
        tr = SanityCheckBatch(result_directory=args.results_dir,
                         project_id=args.project,
                         suite=args.suite,
                         version=args.commit,
                         milestone=args.milestone,
                         plan=args.plan,
                         buginfo_file=args.buginfo_file)
    elif args.runner == 'autopts':
        tr = AutoPTS(results_file=args.results_file,
                         config=args.config,
                         project_id=args.project,
                         suite=args.suite,
                         version=args.commit,
                         milestone=args.milestone,
                         plan=args.plan)
    else:
        sys.exit("Unknown runner")

    tr.discover()
    tr.configure()
    tr.process()
    tr.upload()

    if args.runner == 'sanitycheck' or args.runner == 'sanitycheckbatch':
        tr.sanitycheck_log()

if __name__ == '__main__':
    main()
