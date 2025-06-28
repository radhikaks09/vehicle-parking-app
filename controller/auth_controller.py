from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/<role>')
def login(role):
    return render_template("login.html", role=role)

@auth_bp.route('/signup')
def signup():
    return render_template("signup.html")