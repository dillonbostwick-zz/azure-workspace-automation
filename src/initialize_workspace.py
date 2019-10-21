import json,adal,requests
from requests.exceptions import HTTPError
import logging

from msrestazure.azure_active_directory import AADTokenCredentials

log = logging.getLogger()

DB_RESOURCE_ID = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Databricks/workspaces/{}'
LIST_NODE_TYPES_ENDPOINT = '/api/2.0/clusters/list-node-types'

# AAD access token is to authentication what management token is to authorization.

def adb_authenticate_client_key(params):
	"""
    Authenticate using service principal w/ key.
    """
	authority_host_uri = 'https://login.microsoftonline.com'
	tenant = params['tenant_id']
	authority_uri = authority_host_uri + '/' + tenant
	resource_uri = params['databricks_resource_id']
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


def adb_authorization_client_key(params):
	"""
    Authenticate using service principal w/ key.
    """
	authority_host_uri = 'https://login.microsoftonline.com'
	tenant = params['tenant_id']
	authority_uri = authority_host_uri + '/' + tenant
	resource_uri = 'https://management.core.windows.net/'
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


def create_and_initialize_databricks_workspace(params):
	aad_token = adb_authenticate_client_key(params).token['access_token']
	mgmt_token = adb_authorization_client_key(params).token['access_token']
	initialize_databricks_workspace(aad_token,mgmt_token,params)
