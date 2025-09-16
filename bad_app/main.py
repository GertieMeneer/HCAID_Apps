from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/get-started")
def get_started():
    return render_template("/get-started.html")

serve(app, port=3000)