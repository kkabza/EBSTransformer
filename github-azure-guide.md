# Deploying ESB Transformer to Azure App Service using GitHub

This guide walks you through setting up GitHub repository for your ESB Transformer code and configuring Azure App Service to automatically deploy from GitHub.

## 1. Push Your Code to GitHub

### Create a GitHub Repository
1. Go to [GitHub](https://github.com/) and sign in
2. Click the "+" icon in the top right and select "New repository"
3. Name your repository (e.g., "esb-transformer")
4. Choose public or private (your preference)
5. Click "Create repository"

### Initialize Git in Your Local Project
```powershell
# Navigate to your project folder
cd C:\work\ESB

# Initialize git repository
git init

# Add all files to git
git add .

# Commit the files
git commit -m "Initial commit of ESB Transformer"

# Add GitHub as remote repository (replace with your repo URL)
git remote add origin https://github.com/YourUsername/esb-transformer.git

# Push your code to GitHub
git push -u origin master
```

### Key Files to Verify Before Pushing

Make sure these files are included in your repository:
- `app.py` - Main Flask application
- `requirements.txt` - With all necessary dependencies
- `.deployment` - Configuration for Azure deployment
- `startup.txt` - Startup command for Azure

## 2. Configure Azure App Service for GitHub Deployment

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your App Service (esb-transformer-app)
3. In the left menu, select "Deployment Center"
4. Choose "GitHub" as the source
5. Click "Authorize" if needed and authenticate with GitHub
6. Select your repository and branch (usually "main" or "master")
7. In the Build Provider section, select "App Service Build Service" 
8. Click "Save" to complete the setup

## 3. Configure Application Settings in Azure

1. In your App Service, go to "Configuration" in the left menu
2. Under "Application settings", add/verify these key settings:
   - `WEBSITES_PORT` = `5000`
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
   - `FLASK_APP` = `app.py`
   - `OPENAI_API_KEY` = your API key
3. Under "General settings":
   - Verify Startup Command is set to: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
4. Click "Save" and wait for the changes to apply

## 4. Trigger Deployment and Monitor

1. **Initial deployment** will start automatically after saving the GitHub configuration
2. For future deployments, simply push changes to your GitHub repository:
   ```
   git add .
   git commit -m "Your update message"
   git push
   ```
3. Monitor deployment status:
   - In Azure Portal, go to your App Service
   - Select "Deployment Center" from the left menu
   - Click on "Logs" to see deployment details

## 5. Verify Deployment

1. After deployment completes, go to your app URL:
   - https://esb-transformer-app.azurewebsites.net
2. If you encounter issues:
   - Check deployment logs for errors
   - Go to "Log stream" in the "Monitoring" section
   - Verify all required files were included in your GitHub repository

## 6. Troubleshooting 502 Errors

If you still see 502 errors after deployment:

1. **Check startup file**: Verify that `app.py` contains a Flask application with the variable name `app`
2. **Dependencies**: Make sure your `requirements.txt` includes all necessary packages
3. **Logs**: Check the logs at https://esb-transformer-app.scm.azurewebsites.net/api/logs/docker
4. **SCM Site**: Access the Kudu service at https://esb-transformer-app.scm.azurewebsites.net
5. **Restart**: Try restarting the App Service after deployment completes

## 7. Additional GitHub Actions Setup (Optional)

For more advanced deployment control, you can set up GitHub Actions:

1. In your GitHub repository, go to "Actions" tab
2. Click "New workflow" and select "Deploy to Azure Web App"
3. Customize the YAML file as needed
4. Commit the workflow file to your repository

This will create a GitHub Actions workflow that deploys your application to Azure App Service whenever you push changes to your repository. 