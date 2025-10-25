# app.py
import os
import sys
from flask import Flask, render_template, send_from_directory
import webbrowser
from threading import Timer

# if using templates/static, Flask default works, but when frozen by PyInstaller
# templates/static live inside temporary folder sys._MEIPASS. We handle that:

if getattr(sys, "frozen", False):
    # running as compiled exe
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

template_folder = os.path.join(base_path, "templates")
static_folder = os.path.join(base_path, "static")

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

@app.route('/')
def index():
    # render template (make sure templates/index.html exists)
    return render_template("index.html")

# example static route (optional)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(static_folder, filename)

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    # open browser after 1 second (gives flask time to start)
    Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=5000)
