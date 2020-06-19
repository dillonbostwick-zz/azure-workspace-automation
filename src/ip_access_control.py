# Provision users/groups via direct invocation of the Databricks SCIM API
# given user/group config (may be exported from AAD)

import requests, json, logging
from requests.exceptions import HTTPError

log = logging.getLogger()
resp_dict_whitelist = {}
resp_dict_blacklist = {}


IP_ACCESS_LIST_ENDPOINT = '/api/2.0/preview/ip-access-lists'
WORKSPACE_CONF_ENDPOINT = '/api/2.0/preview/workspace-conf'


def whitelist_ips(whitelist, ip_access_list_uri, headers):
    for ip_list in whitelist:
        log.info(ip_list["label"])
        res = requests.post(ip_access_list_uri, headers=headers, json={
            'label': ip_list['label'],
            'list_type':ip_list['list_type'],
            'ip_addresses': ip_list['ip_addresses']
        })

    try:
        resp_dict_whitelist = json.loads(res.text)
        res.raise_for_status()
    except HTTPError:\
        log.error('Failed to whitelist - Reason: %s' , resp_dict_whitelist)
    else:
        log.info('Whitelist created %s ' ,resp_dict_whitelist)


def blacklist_ips(blacklist, ip_access_list_uri, headers):
    for ip_list in blacklist:
        log.info(ip_list["label"])
        res = requests.post(ip_access_list_uri, headers=headers, json={
            'label': ip_list['label'],
            'list_type':ip_list['list_type'],
            'ip_addresses': ip_list['ip_addresses']
        })

    try:
        resp_dict_blacklist = json.loads(res.text)
        res.raise_for_status()
    except HTTPError:\
        log.error('Failed to blacklist - Reason: %s' , resp_dict_blacklist)
    else:
        log.info('Blacklist created %s ' ,resp_dict_blacklist)



def enable_ip_access_list(workspace_conf_uri,headers):
    log.info('Enabling ip access list feature')
    res = requests.patch(workspace_conf_uri, headers=headers, json={'enableIpAccessLists': 'true'
        })
    res2 = requests.get(workspace_conf_uri+'?keys=enableIpAccessLists', headers=headers)

    try:
        res2.raise_for_status()
        resp2_dict = json.loads(res2.text)
        isIpAccessListEnabled = resp2_dict['enableIpAccessLists']
        print("\n\nEnabled ip access list: ", isIpAccessListEnabled, '\n\n')
    except HTTPError:
        log.error('Failed to enable ip access list {} - Reason: \n\n{}\n\n')
    else:
        log.info('Enabled ip access list')
        log.info(res2.text)

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
        whitelist_ips(whitelist, ip_access_list_uri, headers)
        blacklist_ips(blacklist, ip_access_list_uri, headers)
