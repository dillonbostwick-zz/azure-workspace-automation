# Provision notebooks, libraries, and jobs to the workspace via the Stack CLI
# https://docs.databricks.com/user-guide/dev-tools/stack.html
# Use this doc to build a StackConfig file

import json, logging
import db_client_utils
import databricks_cli.stack.api as stack_api

log = logging.getLogger()

def run(params):
	db_api_client = db_client_utils.create_client(params['db_host'], params['db_pat'])
	stack_client = stack_api.StackApi(db_api_client)

	with open(params['stack_config_path']) as stack_config_file:
		log.info('Reading stack config')
		stack_config = stack_config_file.read()
		
		log.info('Successfully Read stack config file')
		log.debug(stack_config)
		log.info('Beginning stack deploy')

		res = stack_client.deploy(json.loads(stack_config))
		log.info('Stack deployment to workspace completed successfully. Stack deployment results: \n', res)