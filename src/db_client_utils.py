
import databricks_cli.configure.config as cli_configure
import databricks_cli.configure.provider as config_provider
from databricks_cli.configure.config import provide_api_client

def create_client(host, token):
	username = None
	password = None
	insecure = False

	client_config = config_provider.DatabricksConfig(host, username, password, token, insecure)
	return cli_configure._get_api_client(client_config)
