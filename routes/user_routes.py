from flask import Blueprint, render_template, session, redirect, url_for, flash

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'danger')
        return redirect(url_for('auth.login'))

    return f"<h1>Welcome, User! Your email is {session.get('user_email')}</h1>" # Placeholder