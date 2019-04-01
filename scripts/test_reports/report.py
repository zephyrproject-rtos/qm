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
import argparse

retest_text = "description: subtestcase didn't run: likely the image failed to build or to deploy"

DEBUG = False

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


class Platform():
    def __init__(self, name, group, id):
        self.name = name
        self.group_id = group
        self.id = id


class Platforms(TestRail):

    def __init__(self, project_id):
        super().authorize()

        self.project = project_id
        self.group_id = None
        self.platforms = []

    def get(self):
        configs = self.client.config.get(self.project)

        # search for 'Platforms'
        idx = next((index for (index, d) in enumerate(configs) if d["name"] == "Platforms"), None)
        if idx >= 0:
            self.group_id = configs[idx]['id']
            debug(self.group_id)
            for c in configs[idx]['configs']:
                p = Platform(c['name'], c['group_id'], c['id'])
                self.platforms.append(p)
        else:
            print("Creating new group")
            self.client.config.add_group(project_id=self.project, name="Platforms")
            configs = self.client.config.get(self.project)
            self.group_id = next((index for (index, d) in enumerate(configs) if d["name"] == "Platforms"), None)


    def add(self, platform_name):
        self.client.config.add(self.group_id, platform_name)

    def provides(self, platform_name):
        for p in self.platforms:
            if p.name == platform_name:
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

    def configure(self):
        self.status = Status(self.project_id)
        self.cases = self.client.case.for_project(project_id=self.project_id, suite_id=self.suite)
        
        if not self.plan:
            today = datetime.date.today().strftime("%B %d, %Y")
            self.plan = self.client.plan.add(self.project_id,
                                             "Zephyr Core OS Daily: {} {}".format(self.version, today),
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

    def process(self):

        for result_file in self.result_files:
            config = result_file['platform']
            print("Parsing {}".format(result_file['file']))
            junit_xml = JUnitXml.fromfile(result_file['file'])

            results_to_upload = []
            parents = {}

            for suite in junit_xml:
                for testcase in suite:
                    if testcase.result and testcase.result.type == 'skipped':
                        continue

                    ref = self.get_case_name(testcase.name)


                    # if test is skipped, keep it as such, otherwise look at parent results
                    if  testcase.result:
                        tc = testcase
                    elif testcase.name in parents:
                        tc = parents[testcase.name]
                    else:
                        parent = self.find_parent_in_junit(junit_xml, testcase.name)
                        if parent:
                            debug("--> found parent failure: %s -> %s" %(parent.name, parent.result) )

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
                            elif tc.result.type == 'skipped':
                                test_status = self.status.SKIPPED
                            elif tc.result.type == 'failure':
                                test_status = self.status.FAILED
                            else:
                                test_status = self.status.RETEST

                            status_text = tc.result.type

                        cr['status_id'] = test_status
                    else:
                        cr['status_id'] = self.status.PASSED
                        status_text = 'passed'

                    debug("{}: {} => {}".format(config, testcase.name, status_text))
                    if filtered == "" and infra_issue:
                        cr['comment'] = "Infrastructure issue, please retest."
                    else:
                        cr['comment'] = filtered

                    cr['version'] = self.version
                    results_to_upload.append(cr)

            tmp_res = []
            tids =[]

            for result in results_to_upload:
                print(result)
                ref = result['ref']
                case_id = self.get_case_id(ref)
                print(case_id)
                if case_id:
                    tids.append(case_id)

                    result['case_id'] = case_id
                    del result['ref']
                    tmp_res.append(result)

            entry = {
                "include_all": False,
                "case_ids": tids,
                "config_ids": [result_file['id']],
            }
            self.final_results.append({'config': config, 'results': tmp_res, 'run_entry': entry, 'config_id': result_file['id']})

        for fr in self.final_results:
            print("Creating plan configuration")
            self.config_ids.append(fr['config_id'])
            self.runs.append(fr['run_entry'])

        self.plan_entries = self.client.plan.add_entry(self.plan['id'], self.suite, 'Test Run {}'.format(self.version) ,
                                                         config_ids=self.config_ids, runs=self.runs)

    def upload(self):
        plan = self.client.plan.get(self.plan['id'])

        runs = []
        for entry in plan['entries']:
            runs = entry['runs']

        for rr in self.final_results:
            for r in runs:
                if r['config'] == rr['config']:
                    print("Submitting results for {}".format(rr['config']))
                    self.client.result.add_for_cases(r['id'], rr['results'] )

class TCF(TestRun):

    def __init__(self, result_directory, project_id, version, suite, milestone):
        super().__init__()
        super().authorize()

        self.project_id = project_id
        self.version = version
        self.suite = suite
        self.milestone = milestone

        self.variants = ['zephyr', 'espressif']

        self.results_directory = result_directory

    def get_case_name(self, name):
        return name.split("#")[1]

    def find_parent_in_junit(self, junit_xml, name):

        testp, ref = name.split("#")

        for suite in junit_xml:
            for testcase in suite:
                p = self.get_case_name(testcase.name)
                ref_parent = ".".join(ref.split(".")[:-1])
                name = "{}#{}".format(testp, ref_parent)

                if testcase.name == name and testcase.result and testcase.result.type == 'error' and testcase.result.type != 'skipped':
                    return testcase

        return None

    def get_case_text(self, text):
        filtered = []
        for l in text.split("\n"):
            if "console output:" in l:
                new = re.sub(".* console output:", "", l)
                trimmed = re.sub("/home/jenkins.*zephyr.git", "zephyr.git", new)
                filtered.append(trimmed)

        result = "\n".join(filtered)

        return result

    def discover(self):

        for variant in self.variants:
            for j in glob.glob("{}/*{}__zephyr*.xml".format(self.results_directory, variant)):

                file = os.path.basename((j))
                file_meta = file.split("__")

                platform = file_meta[0].replace("junit-", "")

                if platform != 'static':
                    self.result_files.append({"file": j, "platform": platform})

        # Get platforms from project
        p = Platforms(project_id=self.project_id)
        p.get()

        # See if we need to create new configurations for platforms on project
        for rf in self.result_files:
            platform = rf['platform']
            if p.provides(platform_name=platform) == 0:
                print("Need to create new platform %s" % rf['platform'])
                p.add(platform)

        # update
        p.get()
        for rf in self.result_files:
            rf['id'] = p.provides(rf['platform'])


class SanityCheck(TestRun):

    def __init__(self, results_file, config, project_id, version, suite, milestone, plan):
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

    def get_case_name(self, name):
        return name

    def find_parent_in_junit(self, junit_xml, name):
        return None

    def get_case_text(self, text):
        return text

    def discover(self):

        self.result_files.append({"file": self.results_file, "platform": self.config})

        # Get platforms from project
        p = Platforms(project_id=self.project_id)
        p.get()


        if p.provides(platform_name=self.config) == 0:
            print("Need to create new platform %s" % self.config)
            p.add(self.config)

        # update
        p.get()
        for rf in self.result_files:
            rf['id'] = p.provides(self.config)

def parse_args():
    parser = argparse.ArgumentParser(
                description="Upload test results testrail")

    parser.add_argument('-j', '--junit-dir', default=None,
            help="Directory with junit files")

    parser.add_argument('-f', '--junit-file', default=None,
            help="File with test results in junit format.")

    parser.add_argument('-c', '--config', default=None,
            help="Configuration name.")

    parser.add_argument('-V', '--commit', default=None,
        help="Version being tested (git desribe string)")

    parser.add_argument('-p', '--project', type=int, help="Project ID")
    parser.add_argument('-s', '--suite', type=int, help="Suite ID")
    parser.add_argument('-n', '--dry-run', action="store_true", help="Dry run")
    parser.add_argument("-m", "--milestone", type=int, help="Milestone ID")

    parser.add_argument('-P', '--plan', type=int, help="Test plan ID")

    return parser.parse_args()

def main():
    args = parse_args()





    # Discover Restuls
    tr = SanityCheck(results_file=args.junit_file,
                     config=args.config,
                     project_id=args.project,
                     suite=args.suite,
                     version=args.commit,
                     milestone=args.milestone,
                     plan=args.plan)




    tr.discover()
    tr.configure()
    tr.process()
    tr.upload()


if __name__ == '__main__':
    main()
