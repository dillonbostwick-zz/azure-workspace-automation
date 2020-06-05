# Provision users/groups via direct invocation of the Databricks SCIM API
# given user/group config (may be exported from AAD)

import requests, json, logging
from requests.exceptions import HTTPError

log = logging.getLogger()
group_dict = {}


# patch - https://{{workspaceUrl}}/api/2.0/preview/workspace-conf
# get - https://{{workspaceUrl}}/api/2.0/preview/workspace-conf?keys=enableIpAccessLists
# white post - https://{{workspaceUrl}}/api/2.0/preview/ip-access-lists
# black post - https://{{workspaceUrl}}/api/2.0/preview/ip-access-lists


IP_ACCESS_LIST_ENDPOINT = '/api/2.0/preview/ip-access-lists'
WORKSPACE_CONF_ENDPOINT = '/api/2.0/preview/workspace-conf'


def whitelist_ips(whitelist, ip_access_list_uri, headers):
    log.info('Whitelisting ips: ' + whitelist['ip_addresses'])
    res = requests.post(ip_access_list_uri, headers=headers, json={
        'label': whitelist['label'],
        'list_type':whitelist['list_type'],
		'ip_addresses':[
			whitelist['ip_addresses']
		]

	})

	try:
		res.raise_for_status()
	except HTTPError:
		log.error('Failed to whitelist {} - Reason: \n\n{}\n\n'.format(whitelist['label'], res.content))
	else:
		log.info('Whitelist created ' + whitelist['label'] + ' having ips ' + whitelist['ip_addresses'])



def blacklist_ips(blacklist, ip_access_list_uri, headers):
	log.info('Blacklisting ips: ' + blacklist['ip_addresses'])
	res = requests.post(ip_access_list_uri, headers=headers, json={
        'label': blacklist['label'],
        'list_type':blacklist['list_type'],
		'ip_addresses':[
			blacklist['ip_addresses']
		]

	})

	try:
		res.raise_for_status()
	except HTTPError:
		log.error('Failed to whitelist {} - Reason: \n\n{}\n\n'.format(blacklist['label'], res.content))
	else:
		log.info('Blacklist created ' + blacklist['label'] + ' having ips ' + blacklist['ip_addresses'])


def enable_ip_access_list(workspace_conf_uri,headers):
    log.info('Enabling ip access list feature')
    res = requests.patch(workspace_conf_uri, headers=headers, json={
        {
            'enableIpAccessLists': 'true'
        }
    })

    try:
        res.raise_for_status()
    except HTTPError:
        log.error('Failed to enable ip access list {} - Reason: \n\n{}\n\n'.format(res.content))
    else:
        log.info('Enabled ip access list ' , res.content)

def run(params):
	headers = {
		'Authorization': 'Bearer ' + params['db_pat'],
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	ip_access_list_uri = params['db_host'] + IP_ACCESS_LIST_ENDPOINT
	workspace_conf_uri = params['db_host'] + WORKSPACE_CONF_ENDPOINT

	with open(params['ip_access_list_path']) as ip_access_list_file:
		ip_access_list_json = ip_access_list_file.read()
		ip_access_list = json.loads(ip_access_list_json)
		whitelist = ip_access_list['whitelist']
		log.info('Read ' + str(len(whitelist)) +' whitelist')
		blacklist = ip_access_list['blacklist']
		log.info('Read ' + str(len(blacklist)) + ' blacklist')
        enable_ip_access_list(workspace_conf_uri, headers)
        # whitelist_ips(whitelist, ip_access_list_uri, headers)
        # blacklist_ips(blacklist, ip_access_list_uri, headers)
