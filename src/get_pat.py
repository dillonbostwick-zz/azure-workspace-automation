# Get personal access token by first retrieving AAD token via ADAL
# then use it to retrieve a pat (cli
# may not support aad token so a pat is required)


from msrestazure.azure_active_directory import AADTokenCredentials
from requests.exceptions import HTTPError
import json,adal,requests
import logging
from src.get_aad_token import get_adb_authentication_client_key

log = logging.getLogger()

CREATE_TOKEN_ENDPOINT = '/api/2.0/token/create'
REDIRECT_URI = 'http://localhost'

def pat_from_aad_token(aad_token,db_host):
	log.debug('aad: {}'.format(aad_token))
	log.debug('mgmt: {}'.format(db_host))
	uri = db_host + CREATE_TOKEN_ENDPOINT
	log.info('Using host: {}'.format(uri))
	headers = {
		'Authorization': 'Bearer ' + aad_token
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
	# Exchange AAD token for PAT (for use with CLI lib) via Token API
	pat = pat_from_aad_token(aad_token, params['db_host'])
	log.info('Exchanged for PAT: '.format(pat))
	return pat