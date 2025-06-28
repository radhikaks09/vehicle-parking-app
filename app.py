from flask import Flask, render_template
from model import db
from controller.auth_controller import auth_bp

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def default():
    return render_template("landing.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)