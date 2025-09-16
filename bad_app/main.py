from flask import Flask, render_template, request, redirect
from waitress import serve

app = Flask(__name__)

user_data = {}

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/get-started")
def get_started():
    return render_template("/get-started.html")

@app.route("/user-data", methods=["POST"])
def user_data():
    username = request.form["username"]
    password = request.form["password"]
    age = request.form["age"]
    use_case = request.form["use_case"]

    if is_empty_or_null(username) or is_empty_or_null(password) or is_empty_or_null(age) or is_empty_or_null(use_case):
        print("send error message")

    return redirect("/home")

@app.route("/home")
def home():
    return render_template("/home.html")

@app.route("/book-confirmation")
def book_confirmation():
    return render_template("/book-confirmation.html")

@app.route("/more-user-data")
def more_user_data():
    return render_template("/more-user-data.html")

def is_empty_or_null(value):
    return value is None or value == ''


serve(app, port=3000)