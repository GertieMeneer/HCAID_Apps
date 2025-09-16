from flask import Flask, render_template, request

app = Flask(__name__)

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
    option1 = request.form.get("dropdown1")
    option2 = request.form.get("dropdown2")
    option3 = request.form.get("dropdown3")
    user_input = request.form.get("inputField")

    return render_template(
        "html/result.html",
        option1=option1,
        option2=option2,
        option3=option3,
        user_input=user_input
    )

if __name__ == "__main__":
    app.run(debug=True)
