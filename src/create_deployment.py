
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource.resources.models import Deployment, DeploymentMode, TemplateLink
import requests, json, logging
from src.get_aad_token import get_adb_authorization_client_key
from requests.exceptions import HTTPError

BASIC_TEMPLATE_URI = 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-databricks-workspace/azuredeploy.json'
CUSTOM_CIDR_TEMPLATE_URI = 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-databricks-workspace-with-custom-vnet-address/azuredeploy.json'
ALL_IN_ONE = 'https://raw.githubusercontent.com/bhavink/azure-workspace-automation/master/examples/standard/vnet_injection_arm_template.json'
log = logging.getLogger()

def run(params):
	credentials = ServicePrincipalCredentials(
		client_id=params['client_id'],
		secret=params['client_secret'],
		tenant=params['tenant_id'],
	)
	resource_client = ResourceManagementClient(credentials, params['subscription_id'])
	log.info('Created service principal, resource manager client')
	
	# Instantiate objs for deployment
	# use_custom_cidr = 'vnet_address_prefix' in params and params['vnet_address_prefix']

	template_uri = ALL_IN_ONE
	template_link = TemplateLink(uri=template_uri)

	log.info('Using template URI: {}'.format(template_uri))
	
	# Deployment request

	deployment_params = {
		'location': {
			'value': params['location']
		},
		'workspaceName': {
			'value': params['workspace_name']
		},
		'pricingTier': {
			'value': params['pricing_tier']
		},
		'nsgName': {
			'value': params['nsg_name']
		},
		'vnetName': {
			'value': params['vnet_name']
		},
		'privateSubnetName': {
			'value': params['private_subnet_name']
		},
		'publicSubnetName': {
			'value': params['public_subnet_name']
		},
		'vnetCidr': {
			'value': params['vnet_cidr']
		},
		'privateSubnetCidr': {
			'value': params['private_subnet_cidr']
		},
		'publicSubnetCidr': {
			'value': params['public_subnet_cidr']
		},
		'enableNoPublicIp': {
			'value': params['enable_npip']
		},
		'createdBy': {
			'value': params['created_by']
		}
	}

	
	deployment_properties = {
		'mode': DeploymentMode.incremental,
		'template_link': template_link,
		'parameters': deployment_params
	}
	log.debug('Deployment properties:', deployment_properties)

	resource_deployment_res = resource_client.deployments.create_or_update(
		params['rg_name'],
		params['deployment_name'],
		deployment_properties
	)
	log.info('Created or updated deployment')
	log.debug('Deployment response: {}'.format(resource_deployment_res))
	workspace_url = get_deployment_status(params)
	return workspace_url


def get_deployment_status(params):
	subscription_id = params['subscription_id']
	rg_name = params['rg_name']
	workspace_name = params['workspace_name']
	mgmt_token = get_adb_authorization_client_key(params).token['access_token']
	log.debug('mgmt: {}'.format(mgmt_token))
	uri = "https://management.azure.com/subscriptions/" + \
		  params['subscription_id'] + "/resourcegroups/" + \
		  params['rg_name'] + "/providers/Microsoft.Databricks/workspaces/" + \
		  params['workspace_name'] + "?api-version=2018-04-01"

	headers = {
		'Authorization': 'Bearer ' + mgmt_token
	}

	res = requests.get(uri, headers=headers)

	try:
		res.raise_for_status()
		resp_dict = json.loads(res.text)
		workspace_url = resp_dict['properties']['workspaceUrl']
		print("\n\nSuccessfully deployed databricks workspace \n\nWorkspace url: ",'https://'+workspace_url, '\n\n')
		return 'https://'+workspace_url
	except HTTPError:
		print('Failed to deploy databricks workspace - Reason: \n\n', res.content, '\n\n')
		return