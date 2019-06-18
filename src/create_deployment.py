
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource.resources.models import Deployment, DeploymentMode, TemplateLink
import logging

BASIC_TEMPLATE_URI = 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-databricks-workspace/azuredeploy.json'
CUSTOM_CIDR_TEMPLATE_URI = 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-databricks-workspace-with-custom-vnet-address/azuredeploy.json'
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
	use_custom_cidr = 'vnet_address_prefix' in params and params['vnet_address_prefix']
	template_uri = CUSTOM_CIDR_TEMPLATE_URI if use_custom_cidr else CUSTOM_CIDR_TEMPLATE_URI
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
		}
	}
	
	if use_custom_cidr:
		deployment_params['vnetAddressPrefix'] = {
			'value': params['vnet_address_prefix']
		}
		log.info('Using custom CIDR range')
	
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

	return 'https://' + params['location'] + '.azuredatabricks.net'