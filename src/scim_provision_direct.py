# Provision users/groups via direct invocation of the Databricks SCIM API
# given user/group config (may be exported from AAD)

import requests, json, logging
from requests.exceptions import HTTPError

log = logging.getLogger()

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
		log.info('Adding group:', group['name'])

		res = requests.post(groups_uri, headers=headers, json={
			'schemas':[
				GROUP_SCHEMA
			],
			'displayName':group['name']
		})

		try:
			res.raise_for_status()
		except HTTPError:
			log.error('Failed to add group {} - Reason: \n\n{}\n\n'.format(group['name'], res.content))
		else:
			log.info('Added group:', group['name'])

def add_users(users, users_uri, headers):
	# Add each user (seperate requests)
	for user in users:
		log.info('Adding user:', user['name'])

		entitlements_arg = [{'value': e} for e in user['entitlements']]

		res = requests.post(users_uri, headers=headers, json={
			'schemas':[
			 	USER_SCHEMA
			],
			'userName':user['name'],
			'entitlements':entitlements_arg
		})

		try:
			res.raise_for_status()
		except HTTPError:
			log.error('Failed to add user {} - Reason: \n\n{}\n\n'.format(user['name'], res.content))
		else:
			log.info('Added user:', user['name'])

def apply_group_memberships(users, groups, users_uri, groups_uri, headers):
	# Get lists of all existing users and groups:

	try:
		log.info('Retrieving list of users')
		all_users_res_raw = requests.get(users_uri, headers=headers)
		all_users = json.loads(all_users_res_raw.text)['Resources']
	except Exception as err:
		log.error('Failed to get list of users id lookups. Unable to link users to groups - Reason: \n\n{}\n\n'.format(err))
		return 1

	# Apply group memberships
	for group in groups:
		log.info('Adding memberships to group ', group['name'])

		member_ids = [get_user_id(member, all_users) for member in group['members']]

		res = requests.post(groups_uri, headers=headers, json={
			'schemas': [
				GROUP_OP_SCHEMA
			],
			'Operations':[{
				'op':'add',
				'value':{
					'members': [{'value': member_id} for member_id in member_ids]
				}
			}]
		})

		try:
			res.raise_for_status()
		except HTTPError:
			log.error('Failed to add all memberships for group', group['name'], ' - Reason: \n\n{}\n\n'.format(res.content))
		else:
			log.info('Added memberships for group: {}'.format(group['name']))

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
		add_users(users, users_uri, headers)
		apply_group_memberships(users, groups, users_uri, groups_uri, headers)
