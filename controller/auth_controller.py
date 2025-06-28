from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from model import db
from model.user import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email, role=role).first()

        if user and check_password_hash(user.password, password):
            flash(f"{role.capitalize()} login successful!", "success")
            session['current_user_id'] = user.id
            return redirect(url_for(f'{role}.dashboard', role=role))
        else:
            flash(f"Invalid {role} credentials!", "error")
            return render_template("login.html", role=role)
            
    return render_template("login.html", role=role)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        pincode = request.form.get('pincode')

        try:
            new_user = User(
                name=name, 
                email=email, 
                password=generate_password_hash(password), 
                address=address, 
                pincode=pincode)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Signup failed: {str(e)}", "error")
            return render_template("signup.html")
        
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('auth.login', role='user'))
    
    return render_template("signup.html")

@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('default'))