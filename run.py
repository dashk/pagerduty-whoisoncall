from argparse import ArgumentParser
from functools import reduce
import requests

CREDENTIALS_PATH = '.credentials'

def get_pager_duty_token():
    with open(CREDENTIALS_PATH) as credentials_file:
        return credentials_file.read()

def get_pd_request_header():
    return {
        'Authorization': 'Token token=' + get_pager_duty_token(),
        'Accept': 'application/vnd.pagerduty+json;version=2'
    }

def get_primary_oncalls_by_escalation_policy(policy_id):
    oncall_info = requests.get(
        'https://api.pagerduty.com/oncalls?time_zone=UTC&escalation_policy_ids%5B%5D=' + policy_id,
        headers=get_pd_request_header()
    ).json()['oncalls']

    primary_oncalls = []
    for oncall_single in oncall_info:
        if oncall_single['escalation_level'] == 1:
            primary_oncalls.append(oncall_single['user']['summary'])
    
    return primary_oncalls

def get_services_oncall_by_service_name(name):
    for service in requests.get(
            'https://api.pagerduty.com/services?time_zone=UTC&sort_by=name%3Aasc&query=' + name + '&include%5B%5D=escalation_policies',
            headers=get_pd_request_header()
        ).json()['services']:
        service_name = service['name']
        escalation_policy_id = service['escalation_policy']['id']

        print('Primary on-call for ' + service_name + ' is: ' + ', '.join(get_primary_oncalls_by_escalation_policy(escalation_policy_id)))



parser = ArgumentParser('Who is on-call bot')
parser.add_argument('--name', help='service name or team name')
args = parser.parse_args()

get_services_oncall_by_service_name(args.name)
