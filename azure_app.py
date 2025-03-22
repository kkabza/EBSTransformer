from flask import Flask

# Create a simple app
app = Flask(__name__)

@app.route('/')
def hello():
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
        </style>
    </head>
    <body>
        <h1>ESB Transformer - Test Deployment</h1>
        
        <div class="card">
            <h2>✅ Application is Running!</h2>
            <p class="success">Deployment successful</p>
            <p>This is a temporary test page to verify the application is running on Azure App Service.</p>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 