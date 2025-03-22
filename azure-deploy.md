# Deploying ESB Transformer to Azure App Service

This guide explains how to deploy the ESB Transformer application to Azure App Service.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription.
2. **Azure CLI**: Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
3. **Git**: Make sure Git is installed on your machine.
4. **OpenAI API Key**: Ensure you have a valid OpenAI API key.

## Step 1: Prepare Your Application

First, create a few important files needed for Azure deployment:

### 1. Create a runtime.txt file

Create a `runtime.txt` file in the root directory:

```
python-3.10
```

### 2. Create a startup.txt file

Create a `startup.txt` file in the root directory:

```
gunicorn --bind=0.0.0.0 --timeout 600 main:app
```

### 3. Update requirements.txt

Ensure your `requirements.txt` file includes all necessary packages including `gunicorn`.

## Step 2: Deploy to Azure using Azure CLI

### 1. Log in to Azure

```bash
az login
```

### 2. Create a Resource Group (if you don't have one already)

```bash
az group create --name esb-transformer-rg --location eastus
```

### 3. Create an App Service Plan

Create a Linux-based App Service Plan:

```bash
az appservice plan create --name esb-transformer-plan --resource-group esb-transformer-rg --sku B1 --is-linux
```

### 4. Create a Web App

Create a Python-based web app:

```bash
az webapp create --resource-group esb-transformer-rg --plan esb-transformer-plan --name esb-transformer-app --runtime "PYTHON:3.10" --deployment-local-git
```

### 5. Configure Environment Variables

Set the necessary environment variables, including your OpenAI API key:

```bash
az webapp config appsettings set --resource-group esb-transformer-rg --name esb-transformer-app --settings OPENAI_API_KEY="your-openai-api-key-here" FLASK_APP=main.py
```

### 6. Configure Startup Command

Ensure the correct startup command is used:

```bash
az webapp config set --resource-group esb-transformer-rg --name esb-transformer-app --startup-file "startup.txt"
```

### 7. Deploy Your Code

#### Option 1: Deploy using Git

Configure local Git deployment:

```bash
az webapp deployment source config-local-git --name esb-transformer-app --resource-group esb-transformer-rg
```

Get the deployment URL:

```bash
az webapp deployment list-publishing-profiles --name esb-transformer-app --resource-group esb-transformer-rg --query "[?publishMethod=='MSDeploy'].publishUrl" -o tsv
```

Add the Azure remote to your Git repository:

```bash
git remote add azure <deployment-url>
git push azure main
```

#### Option 2: Deploy using ZIP deployment

Zip your application files:

```bash
git archive --format zip --output ./app.zip main
```

Deploy the ZIP file:

```bash
az webapp deployment source config-zip --resource-group esb-transformer-rg --name esb-transformer-app --src ./app.zip
```

## Step 3: Verify the Deployment

After deployment, navigate to your web app at:
```
https://esb-transformer-app.azurewebsites.net
```

## Troubleshooting

If you encounter issues with your deployment, check the logs:

```bash
az webapp log tail --name esb-transformer-app --resource-group esb-transformer-rg
```

### Common Issues:

1. **Missing Packages**: Ensure all required packages are in your requirements.txt file.
2. **Environment Variables**: Verify all environment variables are properly set.
3. **Startup Command**: Make sure your startup command correctly points to your application entry point.
4. **File Permissions**: Ensure your application files have the correct permissions.

## Setting Up Continuous Deployment

For continuous deployment from GitHub:

```bash
az webapp deployment source config --name esb-transformer-app --resource-group esb-transformer-rg --repo-url https://github.com/yourusername/your-repo --branch main --git-token <your-github-personal-access-token>
```

## Scaling Your Application

To scale your application:

```bash
az appservice plan update --name esb-transformer-plan --resource-group esb-transformer-rg --sku S1
```

This will upgrade your plan to Standard (S1), which provides more resources and automatic scaling capabilities.

## Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Python on App Service](https://docs.microsoft.com/en-us/azure/app-service/configure-language-python)
- [Troubleshooting App Service](https://docs.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs) 