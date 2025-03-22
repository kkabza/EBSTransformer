from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESB Transformer - Test Page</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #121212;
                color: #e0e0e0;
            }
            h1 {
                color: #4BBEB3;
                border-bottom: 2px solid #4BBEB3;
                padding-bottom: 10px;
            }
            .card {
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .success {
                color: #4BBEB3;
                font-weight: bold;
            }
            .info {
                color: #6c757d;
                font-size: 0.9em;
            }
            button {
                background-color: #4BBEB3;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #3aa99e;
            }
        </style>
    </head>
    <body>
        <h1>ESB Transformer - Test Deployment</h1>
        
        <div class="card">
            <h2>✅ Application is Running!</h2>
            <p class="success">Deployment successful</p>
            <p>This is a test page to verify that the Flask application is running correctly on Azure App Service.</p>
            <p class="info">This confirms that:</p>
            <ul>
                <li>Python environment is working</li>
                <li>Flask is installed and running</li>
                <li>Gunicorn is serving the application</li>
                <li>The app can respond to HTTP requests</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Next Steps</h2>
            <p>Now that the basic application is running, you can:</p>
            <ol>
                <li>Deploy your full application with all templates and static files</li>
                <li>Verify environment variables are set correctly</li>
                <li>Check logs if you encounter any issues</li>
            </ol>
            <p>Server time: <span id="server-time"></span></p>
            <script>
                document.getElementById('server-time').textContent = new Date().toLocaleString();
            </script>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True) 