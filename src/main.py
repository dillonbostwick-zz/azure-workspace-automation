
import os, sys, logging, json
from src import create_deployment,get_aad_tokens, get_pat, scim_provision_direct #, deploy_stack_to_workspace

PARAM_DEFAULTS = {
	'location': 'eastus',
	'rg_name': None,
	'deployment_name': None,
	'workspace_name': None,
	'pricing_tier': 'premium',
	'subscription_id': os.environ.get('AZURE_SUBSCRIPTION_ID'),
	'client_id': os.environ.get('AZURE_CLIENT_ID'),
	'client_secret': os.environ.get('AZURE_CLIENT_SECRET'),
	'tenant_id': os.environ.get('AZURE_TENANT_ID'),
	'databricks_resource_id':None,
	'tenant_name': None,
	'stack_config_path': None,
	'users_groups_path': None,
	'api_version': '2018-04-01',
	'nsg_name': None,
	'vnet_name':None,
	'private_subnet_name': None,
	'public_subnet_name': None,
	'vnet_cidr':None,
	'private_subnet_cidr':None,
	'public_subnet_cidr':None,
	'enable_npip':False,
	'created_by':None
}
SUCCESS_STATE = 'SUCCESS'

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

def get_params_path():
	return sys.argv[1]

def get_input_params(params_path):
	with open(params_path) as params_file:
		params_str = params_file.read()
		return json.loads(params_str)

def sanitize_input_params(input_params):
	sanitized_params = dict()

	for k in PARAM_DEFAULTS:
		if (k in input_params):
			sanitized_params[k] = input_params[k]
			continue

		if PARAM_DEFAULTS[k] is None:
			raise ValueError('{} is a required parameter'.format(k))
		else:
			sanitized_params[k] = PARAM_DEFAULTS[k]
			log.warn('Value for {} was not found. Defaulting to {}'.format(k, PARAM_DEFAULTS[k]))

	return sanitized_params

def run_deployment_all(params):
	log.info('Beginning deploying with params: ', params)

	# workspace hostname returned from create deployment
	params['db_host'] = create_deployment.run(params)
	log.info('create_deployment completed with host: {}'.format(params['db_host']))
	
	params['db_pat'] = get_pat.run(params)
	log.info('get_pat completed with pat: {}'.format(params['db_pat']))
	
	scim_provision_direct.run(params)
	log.info('scim_provision completed')
	#
	# deploy_stack_to_workspace.run(params)
	# log.info('deploy_stack_to_workspace completed')

	params['autodeploy_state'] = SUCCESS_STATE
	return params

def main():
	params_path = get_params_path()
	input_params = get_input_params(params_path)
	params = sanitize_input_params(input_params)
	status = run_deployment_all(params)

	return status

if __name__ == '__main__':
	status = main()
	print('\n\nWorkspace deployed. Status: ', status)
