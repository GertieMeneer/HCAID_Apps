from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("/html/home.html")

@app.route("/about")
def about():
    return render_template("/html/about.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("username")
    return render_template("/html/greeting.html", name=name)

if __name__ == "__main__":
    app.run(debug=True)
