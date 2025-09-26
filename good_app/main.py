from flask import Flask, render_template, request
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

rf = joblib.load("mushroom_rf_model.pkl")
le_y = joblib.load("label_encoder.pkl")

def predict_mushroom(user_input):
    input_df = pd.DataFrame([user_input])

    input_encoded = pd.get_dummies(input_df)

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

    return render_template("html/result.html", prediction=prediction_full, probability=probability)

if __name__ == "__main__":
    app.run(debug=True)
