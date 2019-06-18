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

Start by installing dependencies. Note that you must specify a chromedriver version that aligns with your version of Chrome (note that if you are not using Chrome you will have to manually install an alternate browser driver via Selenium)

`pip install . --chromedriver-version=75`

### Set up your service principle

There are a few prerequisite setups you must take in your Azure portal, that are not automated:

#### Set up an app for AAD token exchange
Follow the steps to create an app in this Google Doc: https://docs.google.com/document/d/11EUHoUpFAcnsStCktLlzapZO_zhqWAI--JZ95JlGOa4/edit#heading=h.2xebghg73fcd

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
cd src
python main.py ../examples/standard/params.json
```

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