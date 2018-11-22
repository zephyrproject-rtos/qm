import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(
            description="Upload results from TCF/plugin")
    parser.add_argument('-a', '--planid', type=int, help="plan ID")
    parser.add_argument('-b', '--boardname', default="frdm_k64f", help="board name")
    parser.add_argument('-c', '--caserefname', default=None, help="case ref name")
    parser.add_argument('-d', '--details', default=None, help="result details")
    parser.add_argument('-m', '--mode', type=int, default = -1, help =
        '''
        operation mode,
            0: batch mode,
            1 : create plan,
            2: create entry for plan,
            3: upload result
        ''')
    parser.add_argument('-n', '--pname', type=int, help="Project name")
    parser.add_argument('-q', '--query', help='''query info: 
        options:
        projects: return projects info
        boards: return boards info
        suites: return test suite name id
        case ref name: return given ref name case id
        board name: return board id
        ''')
    parser.add_argument('-r', '--resultid', type=int, default=1, help="result id")
    parser.add_argument('-s', '--suitename', default="Main", help="suite name")
    parser.add_argument('-t', '--token')

    parser.add_argument('-B', '--batch', default="",help= '''
        batch string
          project_name,plan_name,board_name,suite_name,case_name,result_id,log_file_path 
        ''')
    parser.add_argument('-C', '--caseid', type=int, help="case id")
    parser.add_argument("-P", "--plugin", default="nxp" ,help="plugin slector")
    parser.add_argument('-p', '--project', type=int, help="Project ID")
    parser.add_argument('-T', '--test', type=int, help="test mode")
    
    return parser.parse_args()