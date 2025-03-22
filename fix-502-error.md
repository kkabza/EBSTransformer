# Quick Fix Guide for 502 Error on ESB-Transformer App

Based on common issues with Flask apps on Azure App Service, here are the most likely solutions for your 502 error:

## Priority Fix #1: Update Startup File Configuration

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your App Service (esb-transformer-app)
3. In the left menu, select **Configuration** → **General settings**
4. Look for the **Startup Command** field
5. Change it to: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
   (This assumes your main Flask app is in `app.py` - adjust if different)
6. Click **Save**
7. **Restart** your app service

## Priority Fix #2: Add Gunicorn to Requirements

1. Go to **Advanced Tools (Kudu)** → **Debug console** → **PowerShell**
2. Navigate to `/site/wwwroot`
3. Edit `requirements.txt` using the editor (click pencil icon)
4. Add this line if it doesn't exist:
   ```
   gunicorn==20.1.0
   ```
5. Save the file
6. Go back to App Service and click **Restart**

## Priority Fix #3: Check App Entry Point

1. In Kudu console (from previous step)
2. Verify if you have `app.py` or `main.py`
3. If your main file is not `app.py`, update the startup command accordingly:
   - For `main.py`: Use `gunicorn --bind=0.0.0.0 --timeout 600 main:app`
   - For another file: Use `gunicorn --bind=0.0.0.0 --timeout 600 yourfilename:app`

## Priority Fix #4: Verify Flask App Object

1. In Kudu console
2. Check your main Flask file (`app.py` or `main.py`)
3. Confirm that the Flask application instance is named `app`
4. If it's using a different name (e.g., `application`), update your startup command accordingly:
   - Example: `gunicorn --bind=0.0.0.0 --timeout 600 main:application`

## Priority Fix #5: Add Critical Environment Variables

1. Go back to the Azure Portal
2. Navigate to **Configuration** → **Application settings**
3. Ensure these variables are set:
   - `FLASK_APP` (set to your main file, e.g., `app.py` or `main.py`)
   - `OPENAI_API_KEY` (verify the value is correct)
   - `WEBSITES_PORT` (set to `5000`)
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` (set to `true`)
4. Click **Save**
5. **Restart** your app service

## Test with a Simple App

If the steps above don't work, create a simple test app to verify basic configuration:

1. In Kudu console, create a new file `test_app.py` with:
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! Flask is working."

if __name__ == '__main__':
    app.run()
```

2. Update your startup command to: `gunicorn --bind=0.0.0.0 --timeout 600 test_app:app`
3. Restart your app service
4. If this works, the issue is with your main application code, not the Azure configuration

## View Logs to Pinpoint the Issue

1. In Azure Portal, go to **Monitoring** → **Log stream**
2. Watch for error messages as the app tries to start
3. These messages will help identify exactly what's failing 