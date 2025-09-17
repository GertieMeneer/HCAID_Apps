from flask import Flask, render_template, request
import pandas as pd
import joblib

app = Flask(__name__)

model = joblib.load("random_forest_model.pkl")
label_encoders = joblib.load("label_encoders.pkl")

@app.route("/")
def home():
    return render_template("html/home.html")

@app.route("/bias")
def bias():
    return render_template("html/bias.html")

@app.route("/explainability")
def explainability():
    return render_template("html/explainability.html")

@app.route("/privacy")
def privacy():
    return render_template("html/privacy.html")

@app.route("/predict", methods=["POST"])
def predict():
    genre = request.form.get("genre")
    runtime = request.form.get("runtime")
    emotion = request.form.get("emotion")
    language = request.form.get("language")
    type_ = request.form.get("type")
    rating = request.form.get("rating")
    director = request.form.get("director")

    example = pd.DataFrame([{
        'Genre': genre,
        'Runtime': runtime,
        'Emotion': emotion,
        'Language': language,
        'Type': type_,
        'Rating': rating,
        'Director': director
    }])

    for col in ['Genre','Emotion','Language','Type','Director','Runtime','Rating']:
        if col in label_encoders:
            val = example.at[0, col]
            # handle unseen values
            if val not in label_encoders[col].classes_:
                val = 'Unknown'
            example[col] = label_encoders[col].transform([val])

    pred_name_code = model.predict(example)[0]
    predicted_name = label_encoders['Name'].inverse_transform([pred_name_code])[0]

    return render_template(
        "html/result.html",
        genre=genre,
        runtime=runtime,
        emotion=emotion,
        language=language,
        type=type_,
        rating=rating,
        director=director,
        prediction=predicted_name
    )

if __name__ == "__main__":
    app.run(debug=True)
