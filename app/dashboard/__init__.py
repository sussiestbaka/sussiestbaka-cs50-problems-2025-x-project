from flask import Blueprint, render_template, request, redirect, url_for, flash, session
dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def dashboard_view():
    if 'logged_in' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')  # Render your dashboard template

@dashboard.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
