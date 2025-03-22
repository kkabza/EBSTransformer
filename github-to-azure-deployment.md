# Deploy ESB Transformer from GitHub to Azure App Service

This guide walks you through deploying the ESB Transformer application from GitHub to Azure App Service using GitHub Actions for continuous deployment.

## Prerequisites

1. **GitHub Repository**: Your code pushed to a GitHub repository
2. **Azure Account**: An active Azure subscription
3. **OpenAI API Key**: For the application's AI features

## Step 1: Create Azure Resources

### Log in to Azure

```bash
az login
```

### Create a Resource Group

```bash
az group create --name esb-transformer-rg --location eastus
```

### Create an App Service Plan (Linux)

```bash
az appservice plan create --name esb-transformer-plan --resource-group esb-transformer-rg --sku B1 --is-linux
```

### Create a Web App

```bash
az webapp create --resource-group esb-transformer-rg --plan esb-transformer-plan --name esb-transformer-app --runtime "PYTHON:3.10"
```

### Configure Environment Variables

```bash
az webapp config appsettings set --resource-group esb-transformer-rg --name esb-transformer-app --settings OPENAI_API_KEY="your-openai-api-key-here" FLASK_APP=main.py
```

### Configure Startup Command

```bash
az webapp config set --resource-group esb-transformer-rg --name esb-transformer-app --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 main:app"
```

## Step 2: Configure GitHub Actions for Deployment

### Get the Publish Profile

1. Go to the Azure Portal
2. Navigate to your App Service (esb-transformer-app)
3. In the left menu, select "Get publish profile"
4. Download the file - it contains deployment credentials

### Add the Publish Profile to GitHub Secrets

1. Go to your GitHub repository
2. Click on "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
5. Value: Paste the entire content of the publish profile file you downloaded
6. Click "Add secret"

### Create GitHub Actions Workflow File

Create `.github/workflows/azure-deploy.yml` in your repository with the following content:

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
      
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'esb-transformer-app'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: .
```

## Step 3: Trigger the Deployment

1. Commit and push the workflow file to your repository:

```bash
git add .github/workflows/azure-deploy.yml
git commit -m "Add Azure deployment workflow"
git push
```

2. The deployment will automatically start once you push to the main branch

## Step 4: Monitor the Deployment

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. You should see your workflow running
4. Click on it to view logs and deployment status

## Step 5: Verify the Deployment

Once the deployment is complete, visit your app at:
```
https://esb-transformer-app.azurewebsites.net
```

## Troubleshooting

### Common Issues

1. **Deployment Failures**:
   - Check the GitHub Actions logs for specific errors
   - Verify that all required files are in your repository

2. **Application Crashes**:
   - Check application logs in Azure:
   ```bash
   az webapp log tail --name esb-transformer-app --resource-group esb-transformer-rg
   ```

3. **Missing Packages**:
   - Ensure all dependencies are in requirements.txt
   - Check if any packages need specific build tools

4. **Environment Variables**:
   - Verify all environment variables are set correctly in Azure

## Continuous Deployment

Once set up, any changes pushed to your main branch will automatically trigger a new deployment. The GitHub Actions workflow will:

1. Check out the latest code
2. Install dependencies
3. Deploy to Azure App Service

This ensures your production environment always reflects the latest version of your code.

## Additional Configuration

### Custom Domain

To add a custom domain:

```bash
az webapp config hostname add --webapp-name esb-transformer-app --resource-group esb-transformer-rg --hostname your-domain.com
```

### Enable HTTPS

To enforce HTTPS:

```bash
az webapp update --name esb-transformer-app --resource-group esb-transformer-rg --https-only true
```

### Scaling

To scale up your app:

```bash
az appservice plan update --name esb-transformer-plan --resource-group esb-transformer-rg --sku S1
``` 