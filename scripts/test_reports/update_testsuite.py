#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Intel Corporation
#
# SPDX-License-Identifier: Apache-2.0

# Script to update testsuite in the Testrail.

import sys
import os
import argparse
import csv
sys.path.append(".")
from testrail_client import TestRailClient

DEBUG = False
err_messages = []
testcases_counter = 0
testcases_testrail = 0
testcases_error = 0


def debug(msg):
    if DEBUG:
        print(msg)

class TestRail():

    def __init__(self):
        self.suite = None
        self.project_id = None
        self.plan = None
        self.project = None
        self.user = None
        self.token = None
        self.client = None

    def authorize(self):
        self.project = 'https://zephyrproject.testrail.io'
        self.user = os.environ.get('TESTRAIL_USER', None)
        self.token = os.environ.get('TESTRAIL_TOKEN', None)
        self.client = TestRailClient(self.project, self.user, self.token)

    def receive_cases_suite(self):
        cases_suite = self.client.case.for_project(project_id=self.project_id, suite_id=self.suite)
        return cases_suite

    def receive_sections(self):
        sections = self.client.section.for_suite(project_id=self.project_id, suite_id=self.suite)
        return sections


class TestSuiteUpdate(TestRail):

    def __init__(self, results_file, project_id, suite):
        super().authorize()
        self.suite = suite
        self.project_id = project_id
        self.results_file = results_file
        self.template = 4
        self.type = 7
        self.priority = 2

    def add_testcase(self, sec_id, testcase):
        self.client.case.add(sec_id, testcase, self.template, self.type, self.priority,
                             None, None, testcase)

    def find_section(self, sections, section, section_id=None):
        found_section = None

        for sec in sections:
            if (sec['name'] == section) and (sec['parent_id'] == section_id):
                print("Section or Subsection ID obtained: ", sec['id'])
                found_section = sec

        if found_section:
            return found_section['id']
        else:
            print("Section or Subsection not obtained. Need to add a new one.")
        return None

    def find_case_by_ref(self, suite, ref):
        for case in suite:
            if case['refs'] == ref:
                return case['id']
        return None

    def add_subsection(self, sections, section, section_id, subsection_add):
        add_to_parent = None
        for par in sections:
            if (par['name'] == section) and (par['id'] == section_id):
                add_to_parent = par

        if add_to_parent:
            print("Finded parent ID is: ", add_to_parent['id'])
            self.client.section.add(self.project_id,
                                    description=subsection_add,
                                    suite_id=self.suite,
                                    parent_id=add_to_parent['id'],
                                    name=subsection_add)
            return True
        else:
            print("Parent is not obtained.")
        return False

    def add_section(self, section):
        new_sec = self.client.section.add(self.project_id, description=section,
                                          suite_id=self.suite,
                                          parent_id=None,
                                          name=section)
        if new_sec:
            print("New section added")
            return True
        else:
            print("New section not added")
        return False


def parse_args():
    parser = argparse.ArgumentParser(description="Update testsuite of the TestRail")

    input_file_info = parser.add_argument_group("File with testcases requirements",
                                                       """

    For input necessary to use .csv file with the all testcases
    generated by the "$ sanitycheck --export-tests filename-with-testcases.csv"
                                        """)
    parser.add_argument('-f', '--results-file', default=None,
                        help="File with the list of all testcases.", required=True)

    parser.add_argument('-p', '--project', type=int, help="Project ID", required=True)
    parser.add_argument('-s', '--suite', type=int, help="Suite ID", required=True)

    return parser.parse_args()

def print_log():
    global testcases_counter
    global testcases_testrail
    global testcases_error

    print('\n====================Total summary====================')
    if testcases_testrail != 0:
        print(testcases_testrail, "test case(s) from file already found in the TestRail")
    if testcases_counter != 0:
        print(testcases_counter, "test case(s) from file uploaded")
    if testcases_error != 0:
        print(testcases_error, "test case(s) from file not uploaded")

    print('\n====================Error messages====================')
    error_len = len(err_messages)
    if error_len != 0:
        for i in range(len(err_messages)):
            print(err_messages[i])
    else:
        print("No errors")

    print('\n====================End====================')

def update_testsuite(run, suite, sections, row):
    global testcases_counter
    global testcases_testrail
    testcase_name = row[2]

    print("\nChecking for: ", testcase_name)
    case_id = run.find_case_by_ref(suite, testcase_name)
    if case_id:
        print("=> Found case from file in the TestRail: {}".format(case_id))
        testcases_testrail += 1
    else:
        #Dot counter helps to decide if need to create a subsection
        #Because some test case names consist only from one word like "shell"
        #But typical testcases consist from two or more words
        #like "shell.newshell.test1" and etc.
        #To detect one word test cases necessary to count dots in their names
        dot_counter = testcase_name.count('.')

        section = row[0]
        print("Section: ", section)
        sec_id = run.find_section(sections, section)
        print("sec_id: ", sec_id)

        if dot_counter:
            #That branch will run only if testcase has a section and subsection
            #Name of the test case may be the subsection name at the same time
            #That section and subsection in the testcase
            #may not exist in the TestRail
            #So necessary to decide section, subsection or both of them
            #add to the TestRail
            subsection = row[1]
            print("Subsection: ", subsection)
            if sec_id:
                subsec_id = run.find_section(sections, subsection, sec_id)
                print("subsec_id: ", subsec_id)

                if not subsec_id:
                    print(" ==> No subsection found. Creating {}/{}".format(section, subsection))
                    run.add_subsection(sections, section, sec_id, subsection)
                    sections = run.receive_sections()
                    subsec_id = run.find_section(sections, subsection, sec_id)

                print("=> Adding testcase: ", testcase_name)
                run.add_testcase(subsec_id, testcase_name)
                testcases_counter += 1
            else:
                print(" ==> No section found. Creating {}/{}".format(section, subsection))
                run.add_section(section)
                sections = run.receive_sections()
                sec_id = run.find_section(sections, section)
                run.add_subsection(sections, section, sec_id, subsection)
                sections = run.receive_sections()
                subsec_id = run.find_section(sections, subsection, sec_id)
                print("=> Adding testcase: ", testcase_name)
                run.add_testcase(subsec_id, testcase_name)
                testcases_counter += 1
        else:
            #That branch will run only if testcase
            #has only a section name without testcase name at all
            #It means that testcase consists only from one word
            #For that kind of test case is unable to detect subsection,
            #only section can be detected
            if not sec_id:
                print(" ==> No section found. Creating {}".format(section))
                run.add_section(section)
                sections = run.receive_sections()
                sec_id = run.find_section(sections, section)

            print("=> Adding testcase: ", testcase_name)
            run.add_testcase(sec_id, testcase_name)
            testcases_counter += 1

def main():
    args = parse_args()
    run = TestSuiteUpdate(results_file=args.results_file, project_id=args.project, suite=args.suite)
    cases_suite = run.receive_cases_suite()
    sections = run.receive_sections()

    global testcases_error

    print("Testcases file: ", run.results_file)
    print("Project ID: ", run.project_id)
    print("Suite ID: ", run.suite)
    row_counter = 0

    with open(run.results_file) as csvfile:
        run.authorize()
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            row_counter += 1
            #ignore blank rows in file
            if not ''.join(row).strip():
                continue
            try:
                sections = run.receive_sections()
                cases_suite = run.receive_cases_suite()
                update_testsuite(run, cases_suite, sections, row)
            except:
                err_test_name = row[2]
                err_msg = "ERROR1: Can't add test case {} in row #{}".format(err_test_name, row_counter)
                err_messages.append(err_msg)
                testcases_error += 1


if __name__ == '__main__':
    main()
    print_log()
