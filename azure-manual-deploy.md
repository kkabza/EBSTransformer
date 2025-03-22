# Manual ZIP Deployment to Azure App Service

This guide walks you through manually deploying the ESB Transformer application to Azure App Service using the ZIP deployment method.

## Prerequisites

1. **Azure Account**: An active Azure subscription
2. **Azure Portal Access**: Admin access to create resources
3. **OpenAI API Key**: For the application's AI features
4. **Local Copy of Code**: The ESB Transformer application files on your computer

## Step 1: Create Azure Resources

### Create Resources via Azure Portal

1. **Log in to the Azure Portal**: https://portal.azure.com/

2. **Create a Resource Group**:
   - Click "Resource groups" → "Create"
   - Enter name (e.g., "esb-transformer-rg") 
   - Select region (e.g., "East US")
   - Click "Review + create" → "Create"

3. **Create an App Service Plan**:
   - Search for "App Service Plan" → "Create"
   - Select your subscription and resource group
   - Enter a name (e.g., "esb-transformer-plan")
   - Select "Linux" as OS
   - Select region (same as resource group)
   - Choose pricing tier (at least "Basic B1" recommended)
   - Click "Review + create" → "Create"

4. **Create a Web App**:
   - Search for "Web App" → "Create"
   - Select your subscription and resource group
   - Enter details:
     - Name: A unique name (e.g., "esb-transformer-app")
     - Publish: Code
     - Runtime stack: Python 3.10
     - Operating System: Linux
     - Region: Same as resource group
     - App Service Plan: Select the one created in step 3
   - Click "Review + create" → "Create"

## Step 2: Prepare Your Application

### Create a ZIP File

1. **Open File Explorer** and navigate to your ESB Transformer application folder

2. **Select all files and folders** in the application directory

3. **Right-click** and select "Send to" → "Compressed (zipped) folder"
   
4. **Name the ZIP file** (e.g., "app.zip")

### Ensure Required Files Exist

Make sure your application contains:

- `requirements.txt`: Lists all Python dependencies
- `main.py`: The entry point to your Flask application
- Any configuration files needed by your app

## Step 3: Configure App Settings in Azure

1. **Go to your Web App** in the Azure Portal

2. **Configure Environment Variables**:
   - In the left menu, go to "Settings" → "Configuration"
   - Click "+ New application setting" and add:
     - Name: `OPENAI_API_KEY` 
     - Value: Your OpenAI API key
   - Add another setting:
     - Name: `FLASK_APP`
     - Value: `main.py`
   - Click "Save"

3. **Configure Startup Command**:
   - In the left menu, go to "Settings" → "Configuration"
   - Click "General settings"
   - Under "Startup Command", enter: `gunicorn --bind=0.0.0.0 --timeout 600 main:app`
   - Click "Save"

## Step 4: Deploy the ZIP File

### Option 1: Deploy via Azure Portal

1. **Go to your Web App** in the Azure Portal

2. **Navigate to Deployment Center**:
   - In the left menu, go to "Deployment" → "Deployment Center"
   - Select "Local Git/FTPS" as the source
   - Choose "FTPS credentials"
   - Click "Save"

3. **Deploy the ZIP File**:
   - In the left menu, go to "Deployment" → "Deployment Center"
   - Click on "External" and copy the FTPS endpoint
   - Use an FTP client (e.g., FileZilla) to upload your ZIP file to the `/site/wwwroot` directory
   - Alternatively, use the "Advanced Tools" (Kudu) option to upload your ZIP file

### Option 2: Deploy via Azure CLI

1. **Open Command Prompt** or PowerShell

2. **Log in to Azure** (if you haven't already):
   ```
   az login
   ```

3. **Deploy the ZIP file**:
   ```
   az webapp deployment source config-zip --resource-group esb-transformer-rg --name esb-transformer-app --src path/to/app.zip
   ```

## Step 5: Verify the Deployment

1. **Restart the Web App**:
   - In the Azure Portal, go to your Web App
   - Click "Restart" in the overview page

2. **Check the Logs**:
   - In the left menu, go to "Monitoring" → "Log stream"
   - Check for any errors in application startup

3. **Visit Your App**:
   - Your app should now be accessible at:
   ```
   https://esb-transformer-app.azurewebsites.net
   ```

## Troubleshooting

### Common Issues

1. **Application Fails to Start**:
   - Check the application logs in "Monitoring" → "Log stream"
   - Verify that all dependencies are listed in requirements.txt
   - Ensure the startup command is correct

2. **Missing Environment Variables**:
   - Verify all environment variables are set correctly
   - Check if your application is looking for variables in a .env file that doesn't exist in Azure

3. **Deployment Issues**:
   - Ensure the ZIP file contains all necessary files at the root level
   - Try restarting the web app after deployment

4. **Performance Issues**:
   - Consider upgrading your App Service Plan to a higher tier
   - Check if your application requires more memory or CPU

## Additional Configuration

### Configure Diagnostic Logging

1. Go to your Web App in the Azure Portal
2. In the left menu, go to "Monitoring" → "Diagnostic settings"
3. Enable appropriate logging options

### Scale Your App

1. Go to your App Service Plan in the Azure Portal
2. In the left menu, click "Scale up (App Service plan)"
3. Select a higher tier as needed

### Enable Custom Domain and HTTPS

1. Go to your Web App in the Azure Portal
2. In the left menu, go to "Settings" → "Custom domains"
3. Follow the instructions to add your custom domain
4. Enable HTTPS for secure connections 