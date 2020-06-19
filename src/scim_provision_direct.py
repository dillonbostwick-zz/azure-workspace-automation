# Provision users/groups via direct invocation of the Databricks SCIM API
# given user/group config (may be exported from AAD)

import requests, json, logging
from requests.exceptions import HTTPError

log = logging.getLogger()
group_dict = {}

USERS_ENDPOINT = '/api/2.0/preview/scim/v2/Users'
GROUPS_ENDPOINT = '/api/2.0/preview/scim/v2/Groups'
USER_SCHEMA = 'urn:ietf:params:scim:schemas:core:2.0:User'
GROUP_SCHEMA = 'urn:ietf:params:scim:schemas:core:2.0:Group'
GROUP_OP_SCHEMA = 'urn:ietf:params:scim:api:messages:2.0:PatchOp'

def get_user_id(username, all_users):
	return next(user for user in all_users if user['userName'] == username)['id']

def add_groups(groups, groups_uri, headers):
	# Add each group (seperate requests)
	for group in groups:
		log.info('Adding group: ' + group['name'])

		res = requests.post(groups_uri, headers=headers, json={
			'schemas':[
				GROUP_SCHEMA
			],
			'displayName':group['name']
		})

		try:
			res.raise_for_status()
			resp_dict = json.loads(res.text)
			group_id = resp_dict['id']
			group_dict[group['name']] = group_id
			log.info("groups created: ",group_dict)
		except HTTPError:
			log.error('Failed to add group {} - Reason: \n\n{}\n\n'.format(group['name'], res.content))
		else:
			log.info('Added group: ' + group['name'] + ' having id ' + group_dict[group['name']])


def apply_group_entitlements(groups, groups_uri, headers):
	# update entitlements for each group (separate requests)
	for group in groups:
		log.info('Updating group: ' + group['name'])
		entitlements_arg = [{'value': e} for e in group['entitlements']]
		log.info(entitlements_arg)
		group_id = group_dict[group['name']]
		log.info(group_id)
		log.info(groups_uri+'/'+group_id)

		res = requests.patch(groups_uri+'/'+group_id, headers=headers, json={
			'schemas':[
			 	GROUP_OP_SCHEMA
			],
			'Operations':[{
				'op':'add',
				'value':{
					'entitlements':entitlements_arg
				}
			}]
		})

		try:
			res.raise_for_status()
			log.info(res.text)
		except HTTPError:
			log.error('Failed to update group {} - Reason: \n\n{}\n\n'.format(group['name'], res.content))
		else:
			log.info('Updated entitlements for group: ' + group['name'])


def add_users(users, users_uri, headers):
	# Add each user (separate requests)
	for user in users:
		log.info('Adding user:' + user['name'])

		# in case if you want to set user entitlements, typically we would set entitlements for a group rather than individual users
		# entitlements_arg = [{'value': e} for e in user['entitlements']]
		# group_id = group_dict[group[g] for g in user['groups']]
		groups_arg = [{'value': group_dict[g]} for g in user['groups']]
		log.info(groups_arg)
		res = requests.post(users_uri, headers=headers, json={
			'schemas':[
			 	USER_SCHEMA
			],
			'userName':user['name'],
			'groups':groups_arg
			#,'entitlements':entitlements_arg
		})

		try:
			res.raise_for_status()
		except HTTPError:
			log.error('Failed to add user {} - Reason: \n\n{}\n\n'.format(user['name'] , res.content))
		else:
			log.info('Added user: ' + user['name'])


def run(params):
	headers = {
		'Authorization': 'Bearer ' + params['db_pat'],
		'Content-Type': 'application/scim+json',
		'Accept': 'application/scim+json'
	}
	groups_uri = params['db_host'] + GROUPS_ENDPOINT
	users_uri = params['db_host'] + USERS_ENDPOINT

	with open(params['users_groups_path']) as users_groups_file:
		users_groups_json = users_groups_file.read()
		users_and_groups = json.loads(users_groups_json)
		users = users_and_groups['users']
		log.info('Read ' + str(len(users)) +' users')
		groups = users_and_groups['groups']
		log.info('Read ' + str(len(groups)) + ' users')

		add_groups(groups, groups_uri, headers)
		apply_group_entitlements(groups, groups_uri, headers)
		add_users(users, users_uri, headers)