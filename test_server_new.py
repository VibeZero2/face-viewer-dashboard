from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Server Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; 
                        border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .success { color: green; font-weight: bold; }
            .button { display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px;
                     text-decoration: none; border-radius: 4px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Face Viewer Dashboard - Server Test</h1>
            <p class="success">✅ Server is running successfully!</p>
            <p>If you can see this page, your Flask server is working correctly.</p>
            <p>This is a minimal test server to verify connectivity.</p>
            <a href="/dashboard-preview" class="button">View Dashboard Preview</a>
        </div>
    </body>
    </html>
    """)

@app.route('/dashboard-preview')
def dashboard_preview():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Preview</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .navbar {
                background-color: #343a40;
                padding: 15px;
                color: white;
            }
            .navbar a {
                color: white;
                text-decoration: none;
                margin-right: 15px;
                font-weight: bold;
            }
            .navbar a.active {
                color: #ffc107;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stats-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            .stat-card {
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 15px;
                width: 22%;
                margin-bottom: 15px;
            }
            .stat-card h3 {
                margin-top: 0;
                color: #343a40;
            }
            .stat-card p {
                font-size: 24px;
                font-weight: bold;
                margin: 0;
                color: #007bff;
            }
            .chart-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
            }
            .chart {
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 15px;
                width: 48%;
                margin-bottom: 20px;
                height: 300px;
            }
            .chart h3 {
                margin-top: 0;
                color: #343a40;
            }
            .chart-placeholder {
                background-color: #f8f9fa;
                height: 250px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px dashed #ced4da;
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            <a href="/" class="active">Dashboard</a>
            <a href="/r-analysis">Analytics</a>
            <a href="/participants">Participants</a>
            <a href="/export">Export</a>
            <a href="/admin">Admin</a>
        </div>

        <div class="container">
            <h1>Face Viewer Dashboard</h1>
            
            <div class="stats-container">
                <div class="stat-card">
                    <h3>Total Participants</h3>
                    <p>42</p>
                </div>
                <div class="stat-card">
                    <h3>Total Responses</h3>
                    <p>126</p>
                </div>
                <div class="stat-card">
                    <h3>Avg. Trust Rating</h3>
                    <p>5.2</p>
                </div>
                <div class="stat-card">
                    <h3>Trust SD</h3>
                    <p>1.3</p>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart">
                    <h3>Trust Ratings Distribution</h3>
                    <div class="chart-placeholder">
                        [Trust Histogram Chart]
                    </div>
                </div>
                <div class="chart">
                    <h3>Trust by Face Type</h3>
                    <div class="chart-placeholder">
                        [Trust by Face Type Chart]
                    </div>
                </div>
            </div>
            
            <p><a href="/" style="color: #007bff;">← Back to Test Page</a></p>
        </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    print("Starting server on http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=8080, debug=True)
