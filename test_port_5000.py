from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Flask is working on port 5000!"

if __name__ == '__main__':
    print("Starting Flask on port 5000...")
    app.run(host='0.0.0.0', port=5000)
