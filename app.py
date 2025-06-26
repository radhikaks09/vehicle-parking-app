from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def default():
    return render_template("landing.html")

@app.route('/login/<role>')
def login(role):
    return render_template("login.html", role=role)

@app.route('/signup')
def signup():
    return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)