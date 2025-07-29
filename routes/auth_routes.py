from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def welcome():
    return render_template('auth/welcome.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['is_admin'] = user.is_admin
            session['full_name'] = user.full_name

            flash('Logged in successfully!', 'success')
            
            # if user is admin then go to admin dashboard else go to user dashboard
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            # if user puts wrong credentials then go to login page again
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html') 
    
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        address = request.form['address']
        pincode = request.form['pincode']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different one.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(
            email=email, 
            full_name=full_name, 
            address=address, 
            pincode=pincode
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    # if user logs out then go to login page
    return redirect(url_for('auth.login'))