# app.py
import os
import sys
from flask import Flask, send_from_directory, Response
import webbrowser
from threading import Timer

# Handle PyInstaller _MEIPASS temporary folder
if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Define static folder (optional)
static_folder = os.path.join(base_path, "static")

app = Flask(__name__, static_folder=static_folder)

@app.route('/')
def index():
    # Direct HTML response (since no template folder exists)
    html = """
    <html>
        <head><title>IP Pool Generator</title></head>
        <body style="font-family: sans-serif; margin: 40px;">
            <h1>Welcome to IP Pool Generator</h1>
            <p>Your Flask EXE app is running locally 🚀</p>
        </body>
    </html>
    """
    return Response(html, mimetype='text/html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(static_folder, filename)

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Open browser automatically after 1 second
    Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=5000)
