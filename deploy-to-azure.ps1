# Azure Deployment Script for ESB Transformer
# Run this script after installing Azure CLI

# Variables - modify these values
$subscriptionId = "83bc8111-12e4-4fcb-b778-7d684f1c520a"
$resourceGroup = "esb-transformer-rg"
$location = "eastus"
$appServicePlan = "esb-transformer-plan"
$webAppName = "esb-transformer-app" # must be globally unique
$sku = "B1" # Basic tier
$runtime = "PYTHON:3.10"
$zipFilePath = ".\app.zip" # Path to your zipped application

# Read OpenAI API key from .env file
$envFile = Get-Content .\.env
$openaiApiKey = ($envFile | Where-Object { $_ -match "OPENAI_API_KEY=" }) -replace "OPENAI_API_KEY=", ""
Write-Host "Found OpenAI API key in .env file"

# Login to Azure (this will open a browser window)
Write-Host "Logging in to Azure..."
az login

# Set active subscription
Write-Host "Setting active subscription..."
az account set --subscription $subscriptionId

# Create a resource group
Write-Host "Creating resource group $resourceGroup..."
az group create --name $resourceGroup --location $location --subscription $subscriptionId

# Create an App Service Plan
Write-Host "Creating App Service Plan $appServicePlan..."
az appservice plan create --name $appServicePlan --resource-group $resourceGroup --sku $sku --is-linux --subscription $subscriptionId

# Create a Web App
Write-Host "Creating Web App $webAppName..."
az webapp create --name $webAppName --resource-group $resourceGroup --plan $appServicePlan --runtime $runtime --subscription $subscriptionId

# Configure application settings
Write-Host "Configuring application settings..."
az webapp config appsettings set --name $webAppName --resource-group $resourceGroup --settings FLASK_APP=main.py OPENAI_API_KEY=$openaiApiKey OPENAI_MODEL=gpt-4-turbo --subscription $subscriptionId

# Update web app startup command
Write-Host "Configuring startup command..."
az webapp config set --name $webAppName --resource-group $resourceGroup --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 main:app" --subscription $subscriptionId

# Create a zip file of the application files if it doesn't exist
if (-not (Test-Path $zipFilePath)) {
    Write-Host "Creating zip file from current directory..."
    Compress-Archive -Path .\* -DestinationPath $zipFilePath -Force
}

# Deploy the application
Write-Host "Deploying application from $zipFilePath..."
az webapp deployment source config-zip --name $webAppName --resource-group $resourceGroup --src $zipFilePath --subscription $subscriptionId

# Show deployment URL
$url = "https://$webAppName.azurewebsites.net"
Write-Host "Deployment completed. Your application is available at: $url"

# Open the web app in a browser
Write-Host "Opening application in default browser..."
Start-Process $url 