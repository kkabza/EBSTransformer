# Troubleshooting 502 Bad Gateway Errors on Azure App Service

When you see a 502 Bad Gateway error on your deployed app (`esb-transformer-app.azurewebsites.net`), it typically means the application is failing to start or crashing during initialization. Here are step-by-step troubleshooting solutions:

## 1. Check Application Logs

First, check the application logs to see what's causing the error:

1. Go to the [Azure Portal](https://portal.azure.com/)
2. Navigate to your App Service (esb-transformer-app)
3. In the left menu, select **Monitoring** > **Log stream**
4. Look for error messages that indicate why the application is failing

## 2. Common Causes and Solutions

### Missing Dependencies

**Problem**: Your `requirements.txt` file might be missing dependencies or list incompatible versions.

**Solution**:
- Check if your app needs `gunicorn` (add it to requirements.txt if missing)
- Ensure all dependencies in your local environment are listed in requirements.txt
- Make sure package versions are compatible with Python 3.10

### Incorrect Startup Command

**Problem**: The startup command might not be correctly configured.

**Solution**:
1. Go to **Configuration** > **General settings**
2. Verify the startup command is: `gunicorn --bind=0.0.0.0 --timeout 600 main:app`
3. Make sure your main Flask app is either named `main.py` or the startup command points to the correct file

### Entry Point Issues

**Problem**: Azure can't find the Flask application object.

**Solution**:
1. Ensure your main Python file (usually `main.py`) has a Flask app object named `app`
2. The file structure should match what's expected in the startup command

### Environment Variables

**Problem**: Required environment variables might be missing or incorrect.

**Solution**:
1. Go to **Configuration** > **Application settings**
2. Ensure OPENAI_API_KEY is correctly set
3. Add any other environment variables your app needs

## 3. Advanced Troubleshooting

### Adjust Application Settings

Try these changes in **Configuration** > **Application settings**:

1. Add `SCM_DO_BUILD_DURING_DEPLOYMENT=true` to ensure pip packages are installed
2. Add `PYTHONPATH=/home/site/wwwroot` to ensure Python can find your modules

### Check for Memory/CPU Issues

Your app might be exceeding resource limits on a Basic tier:

1. Go to **Monitoring** > **Metrics**
2. Check CPU Percentage and Memory Percentage
3. If they're consistently high, consider scaling up your App Service Plan

### Enable Application Insights

For more detailed diagnostics:

1. Go to **Monitoring** > **Application Insights**
2. Enable Application Insights if not already enabled
3. Check the detailed logs for application exceptions

## 4. Deployment Verification

### Verify Your Files Were Deployed Correctly

1. Go to **Advanced Tools (Kudu)** > **Debug console** > **PowerShell**
2. Navigate to `/site/wwwroot`
3. Ensure all your application files are present and in the correct structure
4. Check that `requirements.txt` exists and has the correct content

### Test a Simple App

If the complex app is failing, try deploying a simple app first:

1. Create a minimal `main.py` with just a basic Flask hello world
2. Deploy this to verify Azure configuration is correct

## 5. Restart the App Service

Sometimes a restart can resolve issues:

1. Go to your App Service overview page
2. Click **Restart**
3. Wait a few minutes and check if the app becomes accessible

## Next Steps

If these steps don't resolve the issue:
- Create a local Docker container that matches the Azure environment to test locally
- Consider reaching out to Azure Support with the specific error messages from the logs 