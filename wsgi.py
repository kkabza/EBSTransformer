# Import the Flask application and export it as 'app'
from application import flask_app as app

# This is the entry point for Gunicorn
# The 'app' variable is what Gunicorn will look for

if __name__ == '__main__':
    app.run() 