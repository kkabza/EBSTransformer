# Fix ESB Transformer Azure Deployment

This guide provides direct steps to fix the 502 error with your ESB Transformer deployment on Azure.

## 1. Update Application Settings in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "App Services" in the search bar at the top
3. Click on your app service (esb-transformer-app)
4. In the left menu, scroll down to find "Configuration" (under Settings section)

5. Under **General settings** tab:
   - Set **Startup Command** to: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
   - Save changes

6. Under **Application settings** tab (also in Configuration):
   - Add/verify these key settings:
     * `WEBSITES_PORT` = `5000` 
     * `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
     * `FLASK_APP` = `app.py`
     * Make sure your `OPENAI_API_KEY` is set correctly
   - Save changes

## 2. Fix Deployment Package

1. Create a proper ZIP file with all required files:
   ```powershell
   Compress-Archive -Path .\app.py,.\requirements.txt,.\templates,.\static,.\utils,.\uploads,.\schemas,.\schema_uploads,.\xslt,.\utils.py -DestinationPath .\new_app.zip -Force
   ```

2. If you can't find Deployment Center in Azure Portal:
   - Look for "Deployment" in the left menu
   - Or search for "deployment" in the search box at the top of the app service page
   - Try clicking on "Advanced Tools (Kudu)" and look for deployment options there
   - As a last resort, recreate the App Service and upload proper files during creation

## 3. Alternative Deployment Methods

If you can't access deployment options in Azure Portal, try one of these alternatives:

### Option A: Use Azure Storage as Intermediary
1. Upload your ZIP file to Azure Blob Storage
2. Use Azure Cloud Shell to deploy from storage to your app service

### Option B: GitHub Repository
1. Create a GitHub repo with your application
2. Connect your App Service to the GitHub repo for deployment

### Option C: Local FTP
1. Get FTP/FTPS credentials from Publish Profile
2. Use FileZilla or WinSCP to upload files directly to site/wwwroot

## 4. Check the App Version and Fix Configurations for Azure

1. If your app was built with newer Flask (2.3.x) and Python packages, Azure might need configuration updates.

2. Create a `.deployment` file in your project root with:
   ```
   [config]
   SCM_DO_BUILD_DURING_DEPLOYMENT=true
   ```

3. Create `startup.txt` file with:
   ```
   gunicorn --bind=0.0.0.0 --timeout 600 app:app
   ```

4. Make sure these are included in your deployment package

## 5. Check Logs for Specific Errors

Even if you can't find the log stream in Azure Portal, you can check logs by:
1. Looking at the URL: https://esb-transformer-app.scm.azurewebsites.net/api/logs/docker
2. This might provide insight into what's causing the 502 error 