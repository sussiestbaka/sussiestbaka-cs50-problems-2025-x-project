from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..extensions import db
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Handle login logic
        username = request.form.get('username')
        password = request.form.get('password')
        # Query database for user and verify password
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Login successful, redirect to dashboard
            session['logged_in'] = True
            return redirect(url_for('dashboard.dashboard_view'))  # Redirect to dashboard
        else:
            # Login failed, display error message
            flash("Contraseña O Usuario Incorrecto")
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # if request.method == 'POST':
    #     username = request.form.get('username')
    #     password = request.form.get('password')
        
    #     # Check if user already exists
    #     existing_user = User.query.filter_by(username=username).first()
    #     if existing_user:
    #         flash('Username already exists', 'error')
    #         return redirect(url_for('auth.register'))
        
    #     new_user = User(username=username)
    #     new_user.set_password(password)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     return redirect(url_for('auth.login'))
    return render_template('register.html')

