# Fix ESB Transformer 502 Error - Step-by-Step Guide

Follow these precise steps to fix the 502 error with your Azure deployment.

## Step 1: Create a Minimal Test Deployment

Let's first verify Azure configuration with a simple app:

1. Create a new ZIP file containing only these files:
   - `test_app.py` (already created)
   - `requirements.txt` (already updated)

2. **Create the test ZIP file:**
   ```
   Compress-Archive -Path .\test_app.py,.\requirements.txt -DestinationPath .\test_app.zip -Force
   ```

## Step 2: Update Azure Configuration 

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your App Service (esb-transformer-app)
3. In the left menu, go to **Configuration**
4. Under **General settings** tab:
   - Set **Startup Command** to: `gunicorn --bind=0.0.0.0 --timeout 600 test_app:app`
   - Click **Save**

5. Under **Application settings** tab:
   - Add or update these settings:
     * `WEBSITES_PORT` = `5000`
     * `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
     * Keep your existing `OPENAI_API_KEY` setting
   - Click **Save**

## Step 3: Deploy the Test App

1. In the left menu, go to **Deployment Center**
2. Select **ZIP Deploy** (under Local Git)
3. Click **Deploy**
4. Upload the `test_app.zip` file
5. Wait for deployment to complete

## Step 4: Restart and Test

1. Go to the **Overview** page
2. Click **Restart**
3. After restart, click the URL to test your app
4. You should see a "Test Deployment" page with a success message

## Step 5: Deploy Full Application (After Test App Works)

Once the test app works, we'll deploy the full application:

1. Create a proper ZIP file with all required files:
   ```
   Compress-Archive -Path .\app.py,.\requirements.txt,.\templates,.\static,.\utils,.\uploads,.\schemas,.\schema_uploads,.\xslt -DestinationPath .\full_app.zip -Force
   ```

2. Update Azure Configuration:
   - Change **Startup Command** to: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
   - Keep all other settings the same

3. Deploy the full ZIP file using the same process as Step 3
4. Restart the app service

## Common Issues to Check

- Make sure your ZIP file has files in the root, not inside another folder
- Verify `gunicorn` is in your requirements.txt
- Check that the Flask app variable name matches what's in your startup command
- Ensure all required folders (templates, static) are included
- Verify you have administrator access to manage the App Service 