from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Home page
home_page = """
<!doctype html>
<html>
<head>
    <title>Simple Web App</title>
</head>
<body>
    <h1>Welcome to My Web App</h1>
    <form method="POST" action="/submit">
        <label for="username">Enter your name:</label>
        <input type="text" name="username" required>
        <button type="submit">Submit</button>
    </form>
    <br>
    <a href="{{ url_for('about') }}">Go to About Page</a>
</body>
</html>
"""

# About page
about_page = """
<!doctype html>
<html>
<head>
    <title>About</title>
</head>
<body>
    <h1>About This App</h1>
    <p>This is a simple Flask app with two pages.</p>
    <a href="{{ url_for('home') }}">Go back Home</a>
</body>
</html>
"""

# Greeting page
greeting_page = """
<!doctype html>
<html>
<head>
    <title>Greeting</title>
</head>
<body>
    <h1>Hello, {{ name }}!</h1>
    <a href="{{ url_for('home') }}">Go back Home</a>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(home_page)

@app.route("/about")
def about():
    return render_template_string(about_page)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("username")
    return render_template_string(greeting_page, name=name)

if __name__ == "__main__":
    app.run(debug=True)

