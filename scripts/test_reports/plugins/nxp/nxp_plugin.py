import sys
import os
import glob
import logging
import time
import json
import HTMLParser
import coloredlogs
import urllib
import pprint
import yaml
from nxp_argparser import parse_args
from testrail_client import TestRailClient
from plugins.testrail import TestRail
from junit_xml import TestSuite, TestCase
from datetime import datetime

try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO

def get_plugin_name():
	logging.info('check nxp plugin')
	return "nxp"

def get_class_name():
	return "NXP"


def get_files(file_url, proxy=''):
	#proxies = {'http': 'http://www.someproxy.com:3128'}
	if proxy:
		proxies = {'http': proxy}
	else:
		proxies = {}
	filehandle = urllib.urlopen(file_url, proxies=proxies)
	return filehandle


class NXP(TestRail):
	'''
    NXP extension of test rails plugin
	'''
	def __init__(self, argparser, user = "hake.huang@nxp.com"):
		logging.info('init nxp plugin')
		coloredlogs.install()
		iargparser = parse_args()
		if iargparser.token == None:
			logging.info('load security token from local')
			with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"token.txt")) as file:
				iargparser.token = file.read()
		#logging.info('token is %s'%iargparser.token)
		super(NXP, self).__init__()
		self.authorize(user, iargparser.token)
		self.test_mode = iargparser.test
		self.mode = iargparser.mode
		self.pname = iargparser.pname
		self.batch = iargparser.batch
		self.query = iargparser.query
		self.project = iargparser.project
		logging.info('init NXP plugin')

	def process(self, args):
		logging.info('process in NXP plugin')
		logging.info(args)
		#for p in super(NXP, self).list_projects():
		#	super(NXP, self).print_project_info(p)
		if self.test_mode == 1:
			testcase =  self.run_test_get('Zephyr Sandbox')
			ts = TestSuite("test_mode 1", [testcase])
			print(TestSuite.to_xml_string([ts]))
			return True
		elif self.test_mode == 2:
			testcase =  self.run_test_create_plan_and_run_it('Zephyr Sandbox', 'nxp_trial_2')
			ts = TestSuite("test_mode 2", [testcase])
			print(TestSuite.to_xml_string([ts]))
			return True
		elif self.test_mode == 3:
			testcase =  self.run_test_configs('Zephyr Sandbox')
			ts = TestSuite("test_mode 3", [testcase])
			print(TestSuite.to_xml_string([ts]))
			return True
		elif self.test_mode == 4:
			testcase =  self.run_test_get_status()
			ts = TestSuite("test_mode 4", [testcase])
			print(TestSuite.to_xml_string([ts]))
			return True
		elif self.test_mode == 5:
			testcase =  self.run_test_set_result()
			ts = TestSuite("test_mode 5", [testcase])
			print(TestSuite.to_xml_string([ts]))
			return True
		elif self.test_mode == 6:
			testcase =  self.run_test_batch_mode()
			ts = TestSuite("test_mode 6", [testcase])
			print(TestSuite.to_xml_string([ts]))
			return True
		elif self.test_mode == 7:
			testcase =  self.run_test_query()
			ts = TestSuite("test_mode 7", [testcase])
			print(TestSuite.to_xml_string([ts]))
			return True			

		if self.mode == 1:
			self.create_plan(self.pname)
			return True
		elif self.mode == 2:
			self.create_entry_for_plan(project_id, plan_id, board_name, case_ref_names, suite_name)
			return True
		elif self.mode == 3:
			self.add_result_for_run(run_id, case_id, result_id, details)
		elif self.mode == 0:
			if self.batch == "":
				print("need provide parameter by -M ")
				return False
			ret = self.parse_batch_string(self.batch)
			self.batch_plan_entry_result(ret["project_name"], ret["plan_name"],
				ret["board_name"], ret["suite_name"], ret["case_name"], ret["result_id"], ret["log_file_path"])
			return True

		self.query_func()

		return True

	def query_func(self):
		if self.query.upper() == "PROJECTS":
			projs = self.list_projects()
			for proj in projs:
				self.print_project_info(proj)
			return True
		elif self.query.upper() == "BOARDS":
			projs = self.list_projects()
			for proj in projs:
				pp = pprint.PrettyPrinter(indent=4)
				boards = self.get_config_all_items_by_name(proj['id'],"Boards")
				if boards:
					for board in boards:
						pp.pprint(self.toutf8(board))
			return True
		elif self.query.upper() == "STATUS_IDS":
			statuses = self.get_status()
			for i in statuses:
				print("status name: " + i['name'])
				print("status id: "   + i['id'])
			return True
		elif self.query.upper() == "SUITES":
			projs = self.list_projects()
			for proj in projs:
				logging.info(proj)
				suites = self.get_all_suites_by_project_id(proj['id'])
				for su in suites:
					mydict = {unicode(k).encode("utf-8"): unicode(v).encode("utf-8") for k,v in su.iteritems()}
					print("test suite id: " + mydict['id'])
					print("test suite name: " + mydict['name'])
			return True
		elif self.query.upper() == "SECTIONS":
			projs = self.list_projects()
			for proj in projs:
				logging.info(proj)
				sections = self.get_all_sections_by_project_id(proj['id'])
				#print(sections)
				for k,v in sections.iteritems():
					need_tab = False
					if v['parent_id'] and v['parent_id'] != "None":
						print("section parent name is " +  sections[v['parent_id']]['name'])
						need_tab = True
					if need_tab:
						print("\tsection id is " + k)
						print("\tsection name is " + v['name'])
					else:
						print("section id is " + k)
						print("section name is " + v['name'])
			return True
		elif self.query.upper() == "CASES":
			projs = self.list_projects()
			data = {}
			for proj in projs:

				if self.project != proj['id']:
					continue

				logging.info("=========================================")
				logging.info(proj['id'])

				suites = self.get_all_suites_by_project_id(proj['id'])

				for suite in suites :
					logging.info("=========================================")
					logging.info(self.toutf8(suite['name']))
					sections = self.get_all_sections_by_suite_id(proj['id'], suite['id'])

					for section in sections:
						logging.info(section['name'])
						cases = self.get_all_cases_by_project_id(proj['id'], suite['id'])
						for case in cases:
							logging.info("=========================================")
							#logging.info(case)
							logging.info("section name " + section['name'] + " title " + case['title'])
							if section['id'] == case['section_id'] and suite['id'] == case['suite_id']:
								data[case['title']] = section['name']

			with open('data.yml', 'w') as outfile:
				yaml.safe_dump(data, outfile, default_flow_style=False)
			return True		
		else:
			projs = self.list_projects()
			for proj in projs:
				logging.info("=========================================")
				logging.info(proj)
				
				case_id = self.get_case_id_by_ref(self.query, proj['id'])
				if case_id:
					print("case %s id is %s"%(self.query, case_id))
					return True
				'''
				section_id = self.get_section_id_by_name(proj['id'], self.query)
				if section_id:
					print("section %s id is %s"%(self.query, section_id))
					return True					
				'''
				'''
				boards = self.get_config_all_items_by_name(proj['id'],"Boards")
				if boards:
					for board in boards:
						br = self.toutf8(board)
						if br['name'] == self.query:
							print("board id is ", br['id'])
							return True
				'''
			print("sorry we do not find any match")
		return False

	def parse_batch_string(self, batch_string):
		ret = {}
		batch = batch_string.split(",")
		ret["project_name"]  = batch_settings[0]
		ret["plan_name"]     = batch_settings[1]
		ret["board_name"]    = batch_settings[2]
		ret["suite_name"]    = batch_settings[3]
		ret["case_name"]     = batch_settings[4]
		ret["result_id"]     = batch_settings[5]
		ret["log_file_path"] = batch_settings[6]
		return ret


	def create_entry_for_plan(self, project_id, plan_id, board_name, case_ref_names, suite_name = "on the fly"):
		'''
		only support one type of boards config
		'''
		myid = self.get_user_id()
		config_ids = self.get_config_item_id_by_name(project_id, "Boards", board_name)
		logging.info(config_ids)
		caseids = []
		for i in case_ref_names:
			caseids.insert(-1, self.get_case_id_by_ref(i, project_id))
		msuite = self.get_suite_by_name(project_id, suite_name)
		myruns_settings = [{"include_all": False, "case_ids": caseids, "config_ids": [config_ids[0]]}]
		logging.info(myruns_settings)
		mentry = self.add_entry_for_plan(mplan['id'], msuite['id'], "on the fly test " + str(datetime.now()), "on the fly test ", 
			myid, False, caseids, config_ids, myruns_settings)
		logging.info("---------------------")
		logging.info(mentry)

	def add_result_for_run(self, run_id, case_id, result_id, details):
		'''
		add result for run
        :param run_id: run id
        :param case_id: id of case
        :param result_id: id of result pass is 1, fail is 5, skip is 6
        :param details: more details
		'''
		result = self.set_result(run_id, case_id, result_id, 'set result by auto test.\r\n ' + details)
		logging.info(result)

	def create_plan(self, project_name, plan_name = "on the fly"):
		mproj = self.get_project_by_name(project_name)
		mplan = self.create_test_plan(mproj['id'], project_name, plan_name)
		logging.info("create test plan for %s, id is %s", project_name, mplan['id'])
		return mplan['id']
	def batch_plan_entry_result(self, project_name, plan_name, board_name, suite_name, case_name, result_id, log_file_path):
		mproj = self.get_project_by_name(project_name)
		mplan = self.create_test_plan(mproj['id'], project_name, plan_name)
		logging.info("plan is %s", mplan['id'])
		myid = self.get_user_id()
		config_ids = self.get_config_item_id_by_name(mproj['id'], "Boards", board_name)
		logging.info(config_ids)
		caseids = [self.get_case_id_by_ref(case_name, mproj['id'])]
		msuite = self.get_suite_by_name(mproj['id'], suite_name)
		myruns_settings = [{"include_all": False, "case_ids": caseids, "config_ids": [config_ids[0]]}]
		logging.info(myruns_settings)
		mentry = self.add_entry_for_plan(mplan['id'], msuite['id'], case_name + " on " + str(datetime.now()), "",
			myid, False, caseids, config_ids, myruns_settings)
		logging.info(mentry)
		run_id = self.get_run_id_from_entry(mentry)
		run_log_content = ""
		if log_file_path:
			try:
  				file_handler = open(log_file_path,'rb')
			except:
  				file_handler = get_files(log_file_path)
			with file_handler as f:
				run_log_content = f.readlines()
			logging.info(run_log_content)
		result = self.set_result(run_id, caseids[0], result_id, 'set result by auto test.\r\n ' + str(run_log_content))
		return result


	def run_test_configs(self, project_name):
		mstdout = ['']
		test_cases = TestCase('run_test_configs', '', '', mstdout,'')
		mproj = self.get_project_by_name(project_name)
	 	configs = self.get_all_configs(mproj['id'])
	 	for config in configs:
	 		inconfig = config
	 		logging.info("-----------------------------")
	 		logging.info(inconfig['name'])
	 		mstdout.insert(-1, str(inconfig['name']))
	 		logging.info(inconfig['id'])
	 		mstdout.insert(-1, str(inconfig['id']))
	 		for item in inconfig['configs']:
	 			mitems = self.toutf8(item)
	 			logging.info(mitems['id'])
	 			mstdout.insert(-1, mitems['id'])
	 			logging.info(mitems['name'])
	 			mstdout.insert(-1, mitems['name'])
	 		frdmk64f_id = self.get_config_item_id_by_name(mproj['id'], inconfig['name'], "frdm_k64f")
	 		frdmk64_name = self.get_config_item_name_by_id(mproj['id'], inconfig['id'], frdmk64f_id)
	 		logging.info("frdmk64f id is %s"%(frdmk64f_id))
	 		mstdout.insert(-1, "frdmk64f id is %s"%(frdmk64f_id))
	 		if frdmk64f_id == None or frdmk64_name == None:
	 			test_cases.add_failure_info('get_config_item_id_by_name failure')

		return test_cases

	def run_test_batch_mode(self):
		mstdout = ['']
		test_cases = TestCase('run_test_batch_mode', '', '', mstdout,'')
		batch_settings = "Zephyr Sandbox,batch_plan,frdm_k64f,Master,kernel.device.dummy_device,1,log.txt"
		ret = self.parse_batch_string(batch_settings)
		logging.info(ret)
		result = self.batch_plan_entry_result(ret["project_name"], ret["plan_name"],
			ret["board_name"], ret["suite_name"], ret["case_name"], ret["result_id"], ret["log_file_path"])

	 	logging.info("test result %s"%(str(result)))
	 	mstdout.insert(-1, "test result is %s"%(str(result)))
	 	if result == None:
	 		test_cases.add_failure_info('run_test_batch_mode failure')

		return test_cases



	def run_test_create_test_run_base_on_suite(self, project_name, run_name="suite_test_run"):
		mstdout = ['']
		test_cases = TestCase('run_test_add_plan_and_run_it', '', '', mstdout,'')		
		mproj = self.get_project_by_name(project_name)
		msuite = self.get_suite_by_name(mproj['id'], "Master")
		mruns = self.create_test_run_for_suite(mproj['id'], msuite['id'], run_name)
		if mruns == None:
			test_cases.add_failure_info('create_test_run_for_suite failure')
		mstdout.insert(-1, str(mruns['id']))
		return test_cases

	def run_test_get_status(self):
		mstdout = ['']
		test_cases = TestCase('test_get_status', '', '', mstdout,'')		
		
		statuses = self.get_status()
		for i in statuses:
			logging.info(i['name'])
			logging.info(i['id'])

		if statuses == None:
			test_cases.add_failure_info('test_get_status failure')
		mstdout.insert(-1, str(statuses))
		return test_cases

	def run_test_set_result(self):
		mstdout = ['']
		test_cases = TestCase('run_test_set_result', '', '', mstdout,'')

		result = self.set_result(1561, 79, 1, 'set result by auto test.\r\n ' + "put details here")
		if result == None:
			test_cases.add_failure_info('run_test_set_result failure')		
		mstdout.insert(-1, str(result))
		return test_cases



	def run_test_create_plan_and_run_it(self, project_name, plan_name):
		'''
		create test plan and add cases then run, report issues
		'''
		mstdout = ['']
		test_cases = TestCase('run_test_create_plan_and_run_it', '', '', mstdout,'')
		mproj = self.get_project_by_name(project_name)
		mplan = self.create_test_plan(mproj['id'], project_name, plan_name)
		logging.info("plan is %s", mplan['id'])
		myid = self.get_user_id()
		config_ids = self.get_config_item_id_by_name(mproj['id'], "Boards", "frdm_k64f")
		logging.info(config_ids)
		caseids = [self.get_case_id_by_ref('kernel.device.dummy_device', mproj['id'])]
		msuite = self.get_suite_by_name(mproj['id'], "Master")
		myruns_settings = [{"include_all": False, "case_ids": caseids, "config_ids": [config_ids[0]]}]
		logging.info(myruns_settings)
		'''
		def add_entry(self, plan_id, suite_id, name='', description='',
                  assignedto_id=None, include_all=True, case_ids=list(),
                  config_ids=list(), runs=list())
		'''
		mentry = self.add_entry_for_plan(mplan['id'], msuite['id'], "on the fly test " + str(datetime.now()), "on the fly test ", 
			myid, False, caseids, config_ids, myruns_settings)
		logging.info("---------------------")
		logging.info(mentry)
		if mentry == None:
			test_cases.add_failure_info('create test entry failure')
		mstdout.insert(-1, str(mentry))
		run_id = self.get_run_id_from_entry(mentry)
		self.set_result(run_id, caseids[0], 1, 'set result by auto test.\r\n ' + "put details here")

		return test_cases

	def run_test_get(self, project_name):
		'''
		sample test
		'''
		#sys.stderr = stderr_stream
		mstdout = ['']
		mstder = ['']
		test_cases = TestCase('run_test_get', '', '', mstdout,'')
		mproj = self.get_project_by_name(project_name)
		logging.info(mproj)
		mstdout.insert(-1, str(mproj))
		if mproj == None:
			test_cases.add_failure_info('get_project_by_name failure')
		msuite = self.get_all_suites_by_project_id(mproj['id'])
		logging.info(msuite)
		mstdout.insert(-1, str(msuite))
		if msuite == None:
			test_cases.add_failure_info('get_all_suites_by_project_id failure')
		for su in msuite:
		 	cases = self.get_all_cases_by_project_id(mproj['id'], suite_id = su['id'])
		 	#logging.info(cases)
		 	for case in cases:
		 		incase = self.toutf8(case)
		 		logging.info("-----------------------------")
		 		logging.info(incase['refs'])
		 		mstdout.insert(-1, str(incase['refs']))
		 		logging.info(incase['id'])
		 		mstdout.insert(-1, str(incase['id']))
		 		#logging.info(case['name'])
		suite = self.get_suite_by_name(mproj['id'], "Master")
		logging.info(suite)
		mstdout.insert(-1, str(suite))
		plan = self.get_test_plan_by_name(mproj['id'],'nxp_trial_1')
		logging.info(plan)
		mstdout.insert(-1, str(plan))
		cases = self.get_all_cases_by_project_id(mproj['id'],plan['id'])
	 	for case in cases:
	 		incase = self.toutf8(case)
	 		logging.info("-----------------------------")
	 		logging.info(incase['refs'])
	 		mstdout.insert(-1, str(incase['refs']))
	 		logging.info(incase['id'])
	 		mstdout.insert(-1, str(incase['id']))
		return test_cases
	def run_test_query(self):
		mstdout = ['']
		mstder = ['']
		test_cases = TestCase('run_test_get', '', '', mstdout,'')
		self.query = "projects"
		ret = self.query_func()
		mstdout.insert(-1, self.query)
		if ret == None:
			test_cases.add_failure_info('query projects failure')
		self.query = "boards"
		ret = self.query_func()
		mstdout.insert(-1, self.query)
		if ret == None:
			test_cases.add_failure_info('query boards failure')
		self.query = "suites"
		ret = self.query_func()
		mstdout.insert(-1, self.query)
		if ret == None:
			test_cases.add_failure_info('query suites failure')
		self.query = "status_ids"
		ret = self.query_func()
		mstdout.insert(-1, self.query)
		if ret == None:
			test_cases.add_failure_info('query status_ids failure')
		self.query = "kernel.device.dummy_device"
		ret = self.query_func()
		mstdout.insert(-1, self.query)
		if ret == None:
			test_cases.add_failure_info('query case ref failure')
		self.query = "frdm_k64f"
		ret = self.query_func()
		mstdout.insert(-1, self.query)
		if ret == None:
			test_cases.add_failure_info('query board id failure')
		return test_cases