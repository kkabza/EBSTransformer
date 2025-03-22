# Azure Deployment Steps - Quick Guide

This guide provides simplified steps to deploy the ESB Transformer application to Azure using the provided PowerShell script.

## Prerequisites

1. Azure CLI installed
2. Azure account with active subscription
3. PowerShell
4. Your OpenAI API key

## Step 1: Install Azure CLI (if not already installed)

Download and install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

## Step 2: Edit the PowerShell Script

1. Open `deploy-to-azure.ps1` in any text editor
2. Set your OpenAI API key: Replace `your-openai-api-key` with your actual key
3. (Optional) Modify other variables if needed:
   - `$webAppName` (must be globally unique)
   - `$location` (Azure region)
   - `$sku` (pricing tier)

## Step 3: Run the Deployment Script

1. Open PowerShell
2. Navigate to the project directory containing the script
3. Run the script:
   ```
   .\deploy-to-azure.ps1
   ```

## Step 4: Authentication and Deployment

1. When prompted, sign in to your Azure account in the browser window
2. The script will automatically:
   - Create a resource group
   - Create an App Service Plan
   - Create and configure a Web App
   - Package and deploy your application

## Step 5: Verify Deployment

1. Once deployment is complete, the application URL will be displayed
2. The script will attempt to open the URL in your default browser
3. Verify that the application is running correctly

## Troubleshooting

If you encounter issues:

1. Check the script output for error messages
2. Verify that your subscription ID is correct
3. Ensure your OpenAI API key is correct
4. Check the application logs in the Azure Portal:
   - Go to your App Service
   - Select "Log stream" from the left menu

## Additional Configuration

If needed, you can modify settings after deployment:

1. Go to your App Service in the Azure Portal
2. Select "Configuration" to update environment variables
3. Select "Deployment Center" to set up continuous deployment 