# End-to-End Workspace Automation for Azure Databricks

## Project Description
The purpose of this project is to demonstrate how you can deploy, launch, and provision an Azure Databricks workspace with minimal manual interaction.

This source code is meant to be an example of scripts that you may use as inspiration for your own automation project, but can also be used as a complete project of its own under the understanding that your specific environment and automation needs are probably too unique to be genericized by this single repo.

### Why does this matter?
- Serving a large number of end users with a large number of Azure Databricks workspaces
- Reproducibility between dev, QA/UAT, and prod environments
- You can add additional steps to these scripts, such as with Terraform, to provision additional integrations between Azure Databricks and external services

## Prerequisites:

### Installation

1) Install dependencies.

`pip install .`

2) Install chromedriver [here](http://chromedriver.chromium.org/downloads) and add it to your PATH. Note that you must install a driver version that aligns with your current Chrome installation. If you are unable to use Chrome, you must download an alternate headless brwoser driver via Selenium.

### Set up your service principle

There are a few prerequisite setups you must take in your Azure portal, that are not automated:

#### Set up an app for AAD token exchange
Please contact sales@databricks.com for information on how to configure your AAD service principle for AAD based token authentication, a feature in private preview.

## Quick Start:

This quick start is an _example_ consisting of minimum customization. It is recommended that you thoroughly review the parameters and tweak as needed.

First, open `./examples/standard/params.json` with your preferred text editor and replace the following non-defautable variables with your own values:
`location`
`rg_name`
`subscription_id`
`client_id`
`clent_secret`
`tenant_id`
`tenant_name`

Next, run the following:
```
python src/main.py ./examples/standard/params.json
```

Please note that this will invoke Chromer browser (headless chromedriver) that you have configured as part of prerequisites. When the browser comes up, please enter your Azure AD credentials, at present the workflow is divided into 2 distinct phases

1) Using Azure [ResourceManagementClient](https://pypi.org/project/azure-mgmt-resource/) (utilizes azure service principal) provision databricks workspace
2) Using Azure [ADAL](https://github.com/AzureAD/azure-activedirectory-library-for-python), this is an interactive method to obtain an AAD access token. A browser window (chromedriver) is launched, asking users to log in, this generates AAD token which will be then used (programatically) to generate azure databricks platform [token](https://docs.azuredatabricks.net/api/latest/authentication.html#generate-a-token) which can help us invoke databricks [API's](https://docs.azuredatabricks.net/api/latest/index.html)
 

## Parameters guide:

| Key  | Value  |
|---|---|
| location  | Choose from the [following regions](https://docs.azuredatabricks.net/administration-guide/cloud-configurations/regions.html)  |
| rg_name  | Name of the pre-existing parent resource group into which you will deploy Azure Databricks  |
| deployment_name  | Unique name of the Azure Databricks deployment  |
| workspace_name | Unique name of the Azure Databricks workspace |
| pricing_tier | One of "standard" or "premium" |
| vnet_address_prefix | Leave blank for standard. Specify an address prefix for custom CIDR range deployment |
| subscription_id | Found in Azure portal |
| client_id | Found in Azure portal |
| client_secret | Found in Azure portal |
| tenant_id | Found in Azure portal |
| tenant_name | Should look like "{your AAD tenant name}.onmicrosoft.com"  |
| stack_config_path | Path to JSON file listing stack config (for deploying workspace, libraries, etc). See example and [documentation](https://docs.databricks.com/user-guide/dev-tools/stack.html) |
| users_groups_path | Path to JSON file listing users, groups, and memberships. See example |
| log_level | One of "error", "warn", "info", "debug |
