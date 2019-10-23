# Get personal access token by first retrieving AAD token via ADAL
# then use it to retrieve a pat (cli
# may not support aad token so a pat is required)


from msrestazure.azure_active_directory import AADTokenCredentials
from requests.exceptions import HTTPError
import json,adal,requests
import logging


log = logging.getLogger()

AUTHORITY_HOST_URL = 'https://login.microsoftonline.com/'
MANAGEMENT_HOST_URL = 'https://management.core.windows.net/'
DATABRICKS_RESOURCE_ID = '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d'


# TEMPLATE_AUTHZ_URL = ('https://login.windows.net/{}/oauth2/authorize?' +
# 		 'response_type=code&client_id={}&redirect_uri={}&' +
# 		 'state={}&resource={}')

DB_RESOURCE_ID = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Databricks/workspaces/{}'

LIST_NODE_TYPES_ENDPOINT = '/api/2.0/clusters/list-node-types'
CREATE_TOKEN_ENDPOINT = '/api/2.0/token/create'
REDIRECT_URI = 'http://localhost'



def get_adb_authentication_client_key(params):
	"""
    Authenticate using service principal w/ key.
    """
	authority_host_uri = AUTHORITY_HOST_URL
	tenant = params['tenant_id']
	authority_uri = authority_host_uri + '/' + tenant
	resource_uri = DATABRICKS_RESOURCE_ID
	client_id = params['client_id']
	client_secret = params['client_secret']
	context = adal.AuthenticationContext(authority_uri, api_version=None)
	mgmt_token = context.acquire_token_with_client_credentials(resource_uri, client_id, client_secret)
	credentials = AADTokenCredentials(mgmt_token, client_id)
	log.info("created aad authentication token")
	return credentials


'''
The management token is used for the admin login flows (users/service principal with Contributor access)
- If the user/sp does not exist in the workspace, they will be automatically created as an admin user
Using the bearer token (AAD access token) we cannot query the role or permission of the user/sp in the Azure Databricks Resource, 
but using the management token we are able to query AAD for the role of the user/sp
'''


def get_adb_authorization_client_key(params):
	"""
    Authenticate using service principal w/ key.
    """
	authority_host_uri = AUTHORITY_HOST_URL
	tenant = params['tenant_id']
	authority_uri = authority_host_uri + '/' + tenant
	resource_uri = MANAGEMENT_HOST_URL
	client_id = params['client_id']
	client_secret = params['client_secret']
	context = adal.AuthenticationContext(authority_uri, api_version=None)
	mgmt_token = context.acquire_token_with_client_credentials(resource_uri, client_id, client_secret)
	credentials = AADTokenCredentials(mgmt_token, client_id)
	log.info("created management authorization token for databricks resource")
	return credentials


'''
invoke databricks REST api, in this case "list node types" which is one of the simplest and retruns available azure vm types in a workspace and 
while doing so we initalize databricks workspace
'''

def initialize_databricks_workspace(aad_token, mgmt_token,params):
	location = params['location']
	db_host = 'https://'+location+'.azuredatabricks.net'
	subscription_id = params['subscription_id']
	rg_name = params['rg_name']
	workspace_name = params['workspace_name']
	log.debug('aad: {}'.format(aad_token))
	log.debug('mgmt: {}'.format(mgmt_token))

	uri = db_host + LIST_NODE_TYPES_ENDPOINT
	db_resource_id = DB_RESOURCE_ID.format(subscription_id, rg_name, workspace_name)
	log.info('Using Databricks resource id: '.format(db_resource_id))
	log.info('Using host: {}'.format(uri))
	headers = {
		'Authorization': 'Bearer ' + aad_token,
		'X-Databricks-Azure-Workspace-Resource-Id': db_resource_id,
		'X-Databricks-Azure-SP-Management-Token': mgmt_token
	}

	res = requests.get(uri, headers=headers)

	try:
		res.raise_for_status()
		print("\n\nSuccessfully initialized databricks workspace \n\nList available node types: ", res.content, '\n\n')
	except HTTPError:
		print('Failed to initialize databricks workspace - Reason: \n\n', res.content, '\n\n')
		return


def pat_from_aad_token(aad_token,mgmt_token,params):
	location = params['location']
	db_host = 'https://'+location+'.azuredatabricks.net'
	subscription_id = params['subscription_id']
	rg_name = params['rg_name']
	workspace_name = params['workspace_name']
	log.debug('aad: {}'.format(aad_token))
	log.debug('mgmt: {}'.format(mgmt_token))

	uri = db_host + CREATE_TOKEN_ENDPOINT
	db_resource_id = DB_RESOURCE_ID.format(subscription_id, rg_name, workspace_name)
	log.info('Using Databricks resource id: '.format(db_resource_id))
	log.info('Using host: {}'.format(uri))
	headers = {
		'Authorization': 'Bearer ' + aad_token,
		'X-Databricks-Azure-Workspace-Resource-Id': db_resource_id,
		'X-Databricks-Azure-SP-Management-Token': mgmt_token
	}

	log.info("Exchanging AAD token for PAT for further provisioning")
	res = requests.post(uri, headers=headers)

	try:
		res.raise_for_status()
	except HTTPError:
		print('Failed to generate databricks platform access token - Reason: \n\n', res.content, '\n\n')
		return

	log.debug('Full response from PAT request: {}'.format(res))
 	log.debug('Content: {}'.format(res.content))
 	return json.loads(res.content)['token_value']


def run(params):
	log.info('generating AAD authentication token')
	aad_token = get_adb_authentication_client_key(params).token['access_token']
	log.info('generating AAD management authorization token')
	mgmt_token = get_adb_authorization_client_key(params).token['access_token']
	log.info('AAD Management Token: '.format(mgmt_token))
	initialize_databricks_workspace(aad_token, mgmt_token, params)
	log.info('Initializing databricks workspace')
	# Exchange AAD token for PAT (for use with CLI lib) via Token API
	pat = pat_from_aad_token(aad_token, params['db_host'], params['subscription_id'], params['rg_name'],
							 params['workspace_name'])
	log.info('Exchanged for PAT: '.format(pat))
	return pat