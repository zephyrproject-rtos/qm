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
import argparse

client = TestRailClient('https://zephyrproject.testrail.io',
        '<email>',
        '<token>')

statuses = client.case.status()

def get_status(statuses, status_id):

    result = next((item for item in statuses if item["id"] == status_id), False)
    if result:
        return result['label']

def get_status_id(statuses, name):
    for s in statuses:
        if s['name'] == name:
            return s['id']


PASSED = get_status_id(statuses, 'passed')
FAILED = get_status_id(statuses, 'failed')
BLOCKED = get_status_id(statuses, 'blocked')
SKIPPED = get_status_id(statuses, 'skipped')
RETEST= get_status_id(statuses, 'retest')


def eval_results(run_id):

    run = client.run.get(run_id)
    config = run['config']
    print("Results for {}".format(config))
    print("Blocked: {}".format(run['blocked_count']))
    print("Failed: {}".format(run['failed_count']))
    print("Passed: {}".format(run['passed_count']))


    tests = client.test.for_run(run_id)
    rerun = []
    for test in tests:

        status = test['status_id']
        ref = test['refs']
        #print("{}: {}".format(ref, get_status(statuses, status)))
        if status in [2, 4, 5]:
            rerun.append(test['refs'])

    print("Rerun the follow testing and submit results:")
    rerun_filename = "rerun.{}.{}".format(config, run_id)

    with open(rerun_filename, "w") as rerun_file:
        rerun_file.write("-p\n{}\n".format(run['config']))
        rerun_file.write("--device-testing\n")
        rerun_file.write("--detailed-report\n{}.{}.xml\n".format(run['config'], run_id))
        for r in rerun:
            print("- {}".format(r))
            rerun_file.write("--sub-test\n")
            rerun_file.write("{}\n".format(r))

        print("Saved options file for sanitycheck under: {}".format(rerun_filename))

def get_case_id(cases, reference):
    for case in cases:
        if case['refs'] == reference:
            return case

    return None

def update_results(run_id, junit_file, dryrun=False):
    print("Parsing {}".format(junit_file))
    junit_xml = JUnitXml.fromfile(junit_file)

    results_to_upload = []
    tests = client.test.for_run(run_id)

    results_to_upload = []
    for suite in junit_xml:
        for testcase in suite:
            ref = testcase.name
            tr_case = get_case_id(tests, ref)
            status = None


            if tr_case:
                #pprint(tr_case)
                tc = testcase

                cr = {}
                cr['test_id'] = tr_case['id']

                comment = ""
                if tc.result:

                    if tc.result._elem.text:
                        comment = tc.result._elem.text

                    if tc.result.type == 'error':
                        test_status = BLOCKED
                    elif tc.result.type == 'skipped':
                        test_status = SKIPPED
                    elif tc.result.type == 'failure':
                        test_status = FAILED
                    else:
                        test_status = RETEST

                    status = tc.result.type

                    cr['status_id'] = test_status
                else:
                    cr['status_id'] = PASSED
                    status = 'passed'

                print("{} => {}".format(testcase.name, status))
                cr['comment'] = comment


                results_to_upload.append(cr)

            else:
                print("{} not found in suite".format(testcase.name))

        #pprint(results_to_upload)

        if not dryrun:
            client.result.add_multiple(run_id, results_to_upload)



def parse_args():
    parser = argparse.ArgumentParser(
                description="re-run results and upload")

    parser.add_argument('-r', '--run-id', type=int, help="Run ID from testrail")
    parser.add_argument('-u', '--update-results', help="update results from junit file.")
    parser.add_argument('-n', '--dry-run', action="store_true", help="Dry run")

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    if args.run_id:
        if args.update_results:
            update_results(args.run_id, args.update_results, dryrun=args.dry_run)
        else:
            eval_results(args.run_id)






