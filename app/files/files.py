from flask import Blueprint, session, request, redirect, url_for

file_explorer = Blueprint('files', __name__)

@file_explorer.before_request
def check_for_login():
    if 'logged_in' not in session:
        return redirect(url_for('auth.login'))

@file_explorer.route('/index')
def index():
    return "File Explorer Index"


# Add more routes as needed