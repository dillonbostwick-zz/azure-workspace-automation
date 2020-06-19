import adal
import logging
from msrestazure.azure_active_directory import AADTokenCredentials

log = logging.getLogger()


# AAD access token is to authentication what management token is to authorization.

def get_adb_authentication_client_key(params):
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
	print(credentials.token)
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
invoked in main.py
'''
def get_access_tokens(params):
	aad_token = get_adb_authentication_client_key(params).token['access_token']
	mgmt_token = get_adb_authorization_client_key(params).token['access_token']
