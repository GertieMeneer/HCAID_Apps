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

@app.route("/mushroom-questions", methods=["POST"])
def user_movie_data():
    return render_template("/mushroom-questions.html")

@app.route("/prediction")
def prediction():
    return render_template("/prediction.html")

@app.route("/why-these-questions")
def why_these_questions_page():
    return render_template("/questions-info.html")

@app.route("/predict", methods=["POST"])
def result():
    user_input = {
        'cap-diameter': request.form['cap_diameter'],
        'cap-shape': request.form['cap_shape'],
        'cap-surface': request.form['cap_surface'],
        'cap-color': request.form['cap_color'],
        'gill-attachment': request.form['gill_attachment'],
        'gill-spacing': request.form['gill_spacing'],
        'gill-color': request.form['gill_color'],
        'stem-height': request.form['stem_height'],
        'stem-width': request.form['stem_width'],
        'stem-root': request.form['stem_root'],
        'stem-surface': request.form['stem_surface'],
        'stem-color': request.form['stem_color'],
        'veil-type': request.form['veil_type'],
        'veil-color': request.form['veil_color'],
        'has-ring': request.form['has_ring'],
        'ring-type': request.form['ring_type'],
        'spore-print-color': request.form['spore_print_color']
    }

    prediction, probability = predict_mushroom(user_input)

    class_map = {'p': 'Poisonous', 'e': 'Edible'}
    prediction_full = class_map.get(prediction, prediction)

    return render_template("result.html", prediction=prediction_full, probability=probability)

def predict_mushroom(user_input):
    for feature in NUMERIC_FEATURES:
        user_input[feature] = float(user_input[feature])

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