from flask import Flask, render_template, request, redirect, make_response
from waitress import serve

app = Flask(__name__)

user_data = {}

@app.route("/")
def main_page():
    return render_template("main.html")

@app.route("/get-started")
def get_started_page():
    return render_template("/get-started.html")

@app.route("/home")
def home_page():
    username = request.cookies.get('username')
    cart_items = get_shopping_cart_count(username);
    return render_template("/home.html", shopping_cart_items=cart_items)

@app.route("/user-data", methods=["POST"])
def user_data_page():
    username = request.form["username"]
    password = request.form["password"]
    age = request.form["age"]
    use_case = request.form["use_case"]

    if is_empty_or_null(username) or is_empty_or_null(password) or is_empty_or_null(age) or is_empty_or_null(use_case):
        print("send error message")
    
    user_data[username] = {
        "password": password,
        "age": age,
        "use_case": use_case,
        "shopping_cart_items": []
    }

    response = make_response(redirect("/home"))
    response.set_cookie("username", username)
    return response

@app.route("/book-confirmation", methods=["POST"])
def book_confirmation_page():
    return render_template("/book-confirmation.html")

@app.route("/more-user-data", methods=["POST"])
def more_user_data():
    username = request.cookies.get('username')
    action = request.form["action"]
    get_shopping_cart_count(username)       # to add user to user_data if not exists yet
    if action == "deny":
        user_data[username]["shopping_cart_items"].append("book")
        # user does not want the book, so we add it anyway :)
    if action == "confirm":
        user_data[username]["shopping_cart_items"].append("book")

    shopping_cart = get_shopping_cart_count(username)
        
    return render_template("/more-user-data.html", shopping_cart_items=shopping_cart)

@app.route("/user-movie-data", methods=["POST"])
def user_movie_data():
    return render_template("/user-movie-data.html")

@app.route("/prediction")
def prediction():
    return render_template("/prediction.html")

def is_empty_or_null(value):
    return value is None or value == ''

def get_shopping_cart_count(cookie):
    if cookie == None: return 0

    if cookie not in user_data:
        user_data[cookie] = {
            "password": None,
            "age": None,
            "use_case": None,
            "shopping_cart_items": []
        }

    shopping_cart_items = user_data[cookie]["shopping_cart_items"]
    return len(shopping_cart_items)

serve(app, port=3000)