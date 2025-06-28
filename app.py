from flask import Flask, render_template
from model import db
from model.user import User
from werkzeug.security import generate_password_hash
from controller.auth_controller import auth
from controller.admin_controller import admin

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db.init_app(app)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')

def create_admin():
    with app.app_context():
        if not User.query.filter_by(role='admin').first():
            admin = User(
                name='Admin',
                email='parkedadmin@gmail.com',
                password=generate_password_hash('parkedadmin'),
                address='Admin Office',
                pincode='999999',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

@app.route('/')
def default():
    return render_template("landing.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)