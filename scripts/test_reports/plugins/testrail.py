import logging
import pprint
from testrail_client import TestRailClient

def get_plugin_name():
	return "testrail"

def get_class_name():
	return "TestRail"

class TestRail(object):
    """
    Testrail base class
    """
    def __init__(self, project_url = 'https://zephyrproject.testrail.io'):
        '''
        initialize the Test rail base class
        :param project_url:url of testrail
        '''
        self.client = None
        self.project = project_url

    def authorize(self, email, token):
        '''
        authentication to testrail
        :param email: email address
        :param token: token / passwd
        '''
        self.user = email
        self.token = token
        logging.info(self.project)
        logging.info(self.user )
        logging.info(self.token)
        self.client = TestRailClient(self.project, self.user, self.token)

    def process(self, arg):
    	authorize()
    	return

    def toutf8(self, indata):
        '''
        covert the indata dict to utf-8
        :param indata: input data dict
        '''
        if type(indata) is dict:
            mydict = {unicode(k).encode("utf-8"): unicode(v).encode("utf-8") for k,v in indata.iteritems()}
            return mydict
        elif type(indata) is list:
            mylist = [unicode(v).encode("utf-8") for v in indata]
            return mylist
        elif type(indata) is str:
            mystring = unicode(indata).encode("utf-8")
            return mystring
        return indata

    def list_projects(self):
        '''
        list all projects
        '''
    	pl = self.client.project.all()
        pl = pl + self.client.project.all(1)
        return pl

    def print_project_info(self, proj):
        '''
        output the project inforamtion
        :param proj: project dict or a dict list
        '''
        #logging.info(type(proj).__name__)
        if type(proj) is dict:
            mydict = {unicode(k).encode("utf-8"): unicode(v).encode("utf-8") for k,v in proj.iteritems()}
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(mydict)
        elif type(proj) is list:
            for pp in proj:
                self.print_project_info(pp)

    def get_project_by_name(self, proj_name):
        '''
        get project inform by name
        :param proj_name: project name
        '''
        pl = self.list_projects()
        for p in pl:
            mydict = {unicode(k).encode("utf-8"): unicode(v).encode("utf-8") for k,v in p.iteritems()}
            if mydict['name'].upper() == proj_name.upper():
                logging.info("find project for %s"%(proj_name))
                return mydict
            else:
                next
        return None

    def get_suite_by_name(self, proj_id, suite_name):
        '''
        get test suite by name
        :param proj_id: project id
        :param suite_name: name of test suite
        '''
        suites = self.get_all_suites_by_project_id(proj_id)
        for su in suites:
            mydict = {unicode(k).encode("utf-8"): unicode(v).encode("utf-8") for k,v in su.iteritems()}
            if mydict['name'].upper() == suite_name.upper():
                logging.info("find project for %s"%(suite_name))
                return mydict
            else:
                next
        return None

    def get_case_id_by_ref(self, ref, proj_id, suite_id='', section_id='', **filters):
        '''
        get test case id by ref
        :param ref: case ref in zephyr test rail this is a x.x.x string mappped by case path
        :param proj_id: project id
        :param suite_id: id of test suite optional
        :param section_id: id of test section optional
        :param filters: filters optional
        '''
        suites = self.get_all_suites_by_project_id(proj_id)
        for suite in suites:
            cases = self.get_all_cases_by_project_id(proj_id, suite['id'], section_id='', **filters)
            for case in cases:
                incase = self.toutf8(case)
                if incase['refs'] == ref:
                    return incase['id']
        return None

    def get_case_ref_by_id(self, id, proj_id, suite_id='', section_id='', **filters):
        '''
        get test case ref by id
        :param id: case id in zephyr test rail this is a x.x.x string mappped by case path
        :param proj_id: project id
        :param suite_id: id of test suite optional
        :param section_id: id of test section optional
        :param filters: filters optional
        '''
        suites = self.get_all_suites_by_project_id(proj_id)
        for suite in suites:
            cases = self.get_all_cases_by_project_id(proj_id, suite['id'], section_id='', **filters)
            for case in cases:
                incase = self.toutf8(case)
                if incase['id'] == id:
                    return incase['ref']
        return None        

    def get_all_cases_by_project_id(self, proj_id, suite_id, section_id='', **filters):
        return self.client.case.for_project(proj_id, suite_id, section_id='', **filters)

    def get_all_suites_by_project_id(self, proj_id):
        return self.client.suite.for_project(proj_id)

    def get_all_sections_by_suite_id(self, proj_id, suite_id):
        return self.client.section.for_suite(proj_id, suite_id)

    def get_all_sections_by_project_id(self, proj_id):
        suites = self.get_all_suites_by_project_id(proj_id)
        results = {}
        for su in suites:
            mydict = {unicode(k).encode("utf-8"): unicode(v).encode("utf-8") for k,v in su.iteritems()}
            sections = self.get_all_sections_by_suite_id(proj_id, mydict['id'])
            for mysection in sections:
                ms = self.toutf8(mysection)
                results[ms['id']] = {'name' : ms['name'] , 'parent_id' : ms['parent_id']}
        return results


    def get_section_id_by_name(self, project_id, section_names):
        sections_list = self.get_all_sections_by_project_id(project_id)
        names = section_names.split('.')
        names.reverse()
        for k, v in sections_list.iteritems():
            data = v
            for section in names:
                if data['name'].upper() == section.upper():
                    if data['parent_id'] != "None":
                        data = sections_list[data['parent_id']]
                    else:
                        next
                else:
                    data = None
                    break

            if data != None:
                return k

        return None


    def get_test_plan_by_name(self, proj_id, plan_name):
        '''
        get test plan by name
        :param proj_id: project id
        :param plan_name: name of test plan
        '''
        plans = self.client.plan.for_project(proj_id)
        for p in plans:
            mydict = {unicode(k).encode("utf-8"): unicode(v).encode("utf-8") for k,v in p.iteritems()}
            if mydict['name'].upper() == plan_name.upper():
                logging.info("find project for %s"%(plan_name))
                return mydict
            else:
                next
        return None

    def get_config_item_id_by_name(self, proj_id, config_name, item_name):
        '''
        get configuration item lists id by name
        :param proj_id: project id
        :param config_name: name of config
        :param item_name: name of item
        '''
        config_ids = []
        items = self.get_config_all_items_by_name(proj_id, config_name)
        for item in items:
            mitems = self.toutf8(item)
            if mitems['name'] == item_name:
                config_ids.insert(-1, mitems['id'])
        return config_ids

    def get_config_item_name_by_id(self, proj_id, config_id, item_id):
        '''
        get configuration item id by name
        :param proj_id: project id
        :param config_name: name of config
        :param item_name: name of item
        '''
        items = self.get_config_all_items_by_id(proj_id, config_id)
        for item in items:
            mitems = self.toutf8(item)
            if mitems['id'] == item_id:
                return mitems['name']


    def get_config_all_items_by_name(self, proj_id, config_name):
        '''
        get configuration id by name
        :param proj_id: project id
        :param config_name: name of config
        '''
        mconfigs = self.client.config.get(proj_id)
        for config in mconfigs:
            mconfig = config
            if mconfig['name'] == config_name:
                return mconfig['configs']
        return None       

    def get_config_all_items_by_id(self, proj_id, config_id):
        '''
        get configuration id by name
        :param proj_id: project id
        :param config_id: id of config
        '''
        mconfigs = self.client.config.get(proj_id)
        for config in mconfigs:
            mconfig = config
            if mconfig['id'] == config_id:
                return mconfig['configs']
        return None

    def get_user_id(self, email="hake.huang@nxp.com"):
        muser = self.toutf8(self.client.user.by_email(email))
        return muser['id']



    def get_all_configs(self, proj_id):
        '''
        get configuration id by name
        :param proj_id: project id
        '''
        return self.client.config.get(proj_id)
        

    def get_configurations_id_by_name(self, proj_id):
        '''
        get configuration id by name
        :param proj_id: project id
        :param config_name: name of config
        '''
        mconfigs = self.client.config.get(proj_id)
        for config in mconfigs:
            mconfig = self.toutf8(config)
            if mconfig['name'] == config_name:
                return mconfig['id']
        return None

    def get_configurations_name_by_id(self, proj_id, config_id):
        '''
        get configuration id by name
        :param proj_id: project id
        :param config_id: id of config
        '''
        mconfigs = self.client.config.get(proj_id)
        for config in mconfigs:
            mconfig = self.toutf8(config)
            if mconfig['id'] == config_id:
                return mconfig['name']
        return None

    def create_test_run_for_suite(self, proj_id, suite_id, run_name):
        return self.client.run.add(proj_id, suite_id, run_name)

    def create_test_suite(self, proj_id, name, description=None):
         return self.client.suite.add(proj_id, name, description)

    def add_test_suite_as_run_to_plan(self, proj_id, plan_id, suite_id, run_name):
         return self.client.plan.add_entry(proj_id, suite_id, run_name)

    def create_test_plan(self, proj_id, plan_name, description='',
            milestone_id=None, entries=list()):
        plan = self.get_test_plan_by_name(proj_id, plan_name)
        if plan != None:
            return plan
        logging.info("no duplate plan create new one")
        return self.client.plan.add(proj_id, plan_name, description, milestone_id, entries)

    def add_entry_for_plan(self, plan_id, suit_id, name='', description='', 
        assignedto_id=None, include_all=True, case_ids=list(), config_ids=list(), runs=list()):
        return self.client.plan.add_entry(plan_id, suit_id, name , description, 
            assignedto_id, include_all, case_ids, config_ids, runs)

    def get_run_entry_id(self, entry_dict):
        inner_entry_dict = entry_dict
        new_mentry_dict = self.toutf8(inner_entry_dict['runs'][-1])
        return new_mentry_dict['entry_id']

    def get_run_id_from_entry(self, entry_dict):
        inner_entry_dict = entry_dict
        new_mentry_dict = self.toutf8(inner_entry_dict['runs'][-1])
        return new_mentry_dict['id']

    def get_status(self):
        mstatuses = []
        inner_statuses = self.client.statuses.get()
        for i in inner_statuses:
            mstatuses.insert(-1, self.toutf8(i))
        return mstatuses

    def set_result(self, run_id, case_id, status_id=None,
                     comment=None, vesion=None, elapsed=None,
                     defects=None, assignedto_id=None, **kwargs):
        '''
            def add_for_case(self, run_id, case_id, status_id=None,
                     comment=None, vesion=None, elapsed=None,
                     defects=None, assignedto_id=None, **kwargs):
        '''
        return self.client.result.add_for_case(run_id, case_id, 
            status_id, comment, vesion, elapsed, defects, 
            assignedto_id)






