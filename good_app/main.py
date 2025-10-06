from flask import Flask, render_template, request
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

rf = joblib.load("../data/model_files/mushroom_rf_model.pkl")
le_y = joblib.load("../data/model_files/label_encoder.pkl")

NUMERIC_FEATURES = ['cap-diameter', 'stem-height', 'stem-width']

CATEGORICAL_FEATURES = ['cap-shape', 'stem-surface', 'stem-color', 'spore-print-color']

CATEGORY_MAPS = {
    'cap-shape': {'x':'Convex','f':'Flat','s':'Sunken','b':'Bell','o':'Spherical','p':'Plate','c':'Conical','Missing':'Missing'},
    'stem-surface': {'s':'Smooth','y':'Scaly','i':'Indented','t':'Tap','g':'Grooves','k':'Knobbed','f':'Fibrous','h':'Hairy','Missing':'Missing'},
    'stem-color': {'w':'White','n':'Brown','y':'Yellow','g':'Gray','o':'Orange','e':'Red','u':'Purple','f':'Buff','p':'Pink','k':'Black','r':'Green','l':'Lilac','b':'Beige','Missing':'Missing'},
    'spore-print-color': {'k':'Black','p':'Purple','w':'White','n':'Brown','g':'Green','u':'Lilac','r':'Red','Missing':'Missing'}
}

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

@app.route("/")
def home():
    return render_template("html/home.html")

@app.route("/main")
def main():
    return render_template("html/main.html")

@app.route("/info")
def info():
    return render_template("html/info.html")

@app.route("/bias")
def bias():
    return render_template("html/bias.html")

@app.route("/explainability")
def explainability():
    return render_template("html/explainability.html")

@app.route("/privacy")
def privacy():
    return render_template("html/privacy.html")

@app.route("/result", methods=["POST"])
def result():
    user_input = {key: request.form[key] for key in NUMERIC_FEATURES + CATEGORICAL_FEATURES}
    prediction, probability = predict_mushroom(user_input)
    class_map = {'p': 'Poisonous', 'e': 'Edible'}
    prediction_full = class_map.get(prediction, prediction)
    return render_template("html/result.html", prediction=prediction_full, probability=probability)

if __name__ == "__main__":
    app.run(debug=True)
