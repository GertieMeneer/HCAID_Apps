from flask import Flask, render_template, request, redirect, make_response
from waitress import serve
import pandas as pd
import joblib
import numpy as np

rf = joblib.load("../data/model_files/mushroom_rf_model.pkl")
le_y = joblib.load("../data/model_files/label_encoder.pkl")

NUMERIC_FEATURES = ['cap-diameter', 'stem-height', 'stem-width']
CATEGORICAL_FEATURES = [
    'cap-shape', 'cap-surface', 'cap-color', 'gill-attachment', 'gill-spacing', 
    'gill-color', 'stem-root', 'stem-surface', 'stem-color', 'veil-type', 
    'veil-color', 'has-ring', 'ring-type', 'spore-print-color'
]

CATEGORY_MAPS = {
    'cap-shape': {'x':'Convex','f':'Flat','s':'Sunken','b':'Bell','o':'Spherical','p':'Plate','c':'Conical','Missing':'Missing'},
    'cap-surface': {'t':'Tap','s':'Smooth','y':'Scaly','h':'Hairy','g':'Grooves','d':'Dotted','e':'Eroded','k':'Knobbed','i':'Indented','w':'Wrinkled','l':'Layered','Missing':'Missing'},
    'cap-color': {'n':'Brown','y':'Yellow','w':'White','g':'Gray','e':'Red','o':'Orange','r':'Green','u':'Purple','p':'Pink','k':'Black','b':'Buff','l':'Lilac','Missing':'Missing'},
    'gill-attachment': {'a':'Attached','d':'Descending','x':'Unknown','p':'Partial','e':'Evanescent','s':'Split','f':'Free','Missing':'Missing'},
    'gill-spacing': {'c':'Close','d':'Distant','f':'Far','Missing':'Missing'},
    'gill-color': {'w':'White','n':'Brown','y':'Yellow','p':'Pink','g':'Gray','f':'Buff','o':'Orange','k':'Black','r':'Green','e':'Red','u':'Purple','b':'Buff','Missing':'Missing'},
    'stem-root': {'s':'Stemmed','b':'Bulbous','r':'Rooted','f':'Flat','c':'Club','Missing':'Missing'},
    'stem-surface': {'s':'Smooth','y':'Scaly','i':'Indented','t':'Tap','g':'Grooves','k':'Knobbed','f':'Fibrous','h':'Hairy','Missing':'Missing'},
    'stem-color': {'w':'White','n':'Brown','y':'Yellow','g':'Gray','o':'Orange','e':'Red','u':'Purple','f':'Buff','p':'Pink','k':'Black','r':'Green','l':'Lilac','b':'Beige','Missing':'Missing'},
    'veil-type': {'u':'Universal','Missing':'Missing'},
    'veil-color': {'w':'White','y':'Yellow','n':'Brown','u':'Purple','k':'Black','e':'Red','Missing':'Missing'},
    'has-ring': {'t':'Yes','f':'No','Missing':'Missing'},
    'ring-type': {'f':'Flaring','e':'Evanescent','z':'Zone','l':'Large','r':'Ring','p':'Pendant','g':'Girdle','m':'Mini','Missing':'Missing'},
    'spore-print-color': {'k':'Black','p':'Purple','w':'White','n':'Brown','g':'Green','u':'Lilac','r':'Red','Missing':'Missing'}
}

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
        
    return render_template("/user-data.html", shopping_cart_items=shopping_cart)

@app.route("/why-these-questions")
def why_these_questions_page():
    return render_template("/questions-info.html")

# debug endpoint to skip all those annoying popups lol
@app.route("/mushroom-questions")
def mushroom_questions():
    return render_template("mushroom-questions.html", shopping_cart_items=get_shopping_cart_count(request.cookies.get("username")));

@app.route("/mushroom-questions", methods=["POST"])
def user_movie_data():
    return render_template("mushroom-questions.html", shopping_cart_items=get_shopping_cart_count(request.cookies.get("username")))

@app.route("/predict", methods=["POST"])
def result():
    user_input = {key: request.form[key] for key in NUMERIC_FEATURES + CATEGORICAL_FEATURES}
    prediction, probability = predict_mushroom(user_input)
    class_map = {'p': 'Poisonous', 'e': 'Edible'}
    prediction_full = class_map.get(prediction, prediction)
    return render_template("result.html", prediction=prediction_full, probability=probability)

def predict_mushroom(user_input):
    for feature in NUMERIC_FEATURES:
        user_input[feature] = float(user_input[feature])

    for feature in CATEGORICAL_FEATURES:
        value = user_input[feature]
        if value == "" or value is None:
            value = 'Missing'
        user_input[feature] = CATEGORY_MAPS[feature].get(value, 'Missing')

    input_df = pd.DataFrame([user_input])
    input_encoded = pd.get_dummies(input_df, columns=CATEGORICAL_FEATURES)

    missing_cols = set(rf.feature_names_in_) - set(input_encoded.columns)
    for col in missing_cols:
        input_encoded[col] = 0

    input_encoded = input_encoded[rf.feature_names_in_]

    prob = rf.predict_proba(input_encoded)[0]
    pred_index = np.argmax(prob)
    pred_class = le_y.classes_[pred_index]
    confidence = prob[pred_index] * 100

    return pred_class, round(confidence, 2)

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
