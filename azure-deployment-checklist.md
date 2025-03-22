# ESB Transformer Deployment Checklist

This checklist will help ensure successful deployment of the ESB Transformer Flask application to Azure.

## 1. Required Files Check

Ensure these key files are included in your deployment package:

- [ ] `app.py` or `main.py` (your main Flask application file)
- [ ] `requirements.txt` with these packages:
  ```
  flask>=2.0.1
  gunicorn>=20.1.0
  jinja2>=3.0.1
  openai>=1.0.0
  python-dotenv>=0.19.0
  ```
- [ ] `/templates` directory with all HTML templates
- [ ] `/static` directory with CSS and JS files
- [ ] Any other Python modules your app relies on

## 2. ZIP File Preparation

- [ ] Place all files in their correct directories
- [ ] Keep the same directory structure as your local project
- [ ] Create a ZIP file containing all required files and directories
- [ ] Make sure the ZIP file has the correct structure (not a nested folder)

## 3. Azure Configuration

- [ ] Set startup command: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
   (Change `app:app` to match your main Flask file and application variable)

- [ ] Set environment variables:
  - [ ] `OPENAI_API_KEY`
  - [ ] `FLASK_APP` (typically 'app.py' or 'main.py')
  - [ ] `OPENAI_MODEL` (e.g., 'gpt-4-turbo')
  - [ ] `WEBSITES_PORT=5000`
  - [ ] `SCM_DO_BUILD_DURING_DEPLOYMENT=true`

## 4. Deployment Steps

1. Navigate to Azure Portal → App Service
2. Go to your App Service (esb-transformer-app)
3. Go to Deployment Center → Local Git/FTPS/ZIP → ZIP Deploy
4. Upload your ZIP file
5. Wait for the deployment to complete
6. Go to Configuration and set your environment variables
7. Go to General Settings and set your startup command
8. Restart the app service

## 5. Verification

- [ ] Check application logs for errors
- [ ] Test the web application by visiting the URL
- [ ] Verify that all pages are loading correctly
- [ ] Check that templates are rendering properly

## 6. Troubleshooting

If you encounter 502 errors:
1. Check logs for specific error messages
2. Verify gunicorn is in requirements.txt
3. Confirm startup command matches your actual Flask app structure
4. Verify all necessary files are uploaded
5. Check application settings are configured correctly 