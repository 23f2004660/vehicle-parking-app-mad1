# app.py
from ast import Return
from flask import Flask, flash, redirect, render_template, request, session, url_for
# Make sure to import request, redirect, etc. when you need them later
from models.database import db, User, ParkingLot, ParkingSpot, Reservation

app = Flask(__name__)

# --- App Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-super-secret-key'

# Initialize the database with the app
db.init_app(app)

# routes begin here
@app.route('/')
def welcome(): 
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        address = request.form['address']
        pincode = request.form['pincode']

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different one.', 'danger')
            return redirect(url_for('register'))

        # Create new user
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
        return redirect(url_for('login'))
    
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find the user by their email address
        user = User.query.filter_by(email=email).first()

        # Check if the user exists and the password is correct
        if user and user.check_password(password):
            # Store user's info in the session to remember them
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['is_admin'] = user.is_admin

            flash('Logged in successfully!', 'success')
            
            # Redirect to the correct dashboard based on their role
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            # If login fails, show an error message
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))

   return render_template('login.html') 


@app.route('/logout')
def logout():
    session.clear() # Clears all data from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    # Protect this route: only admins should see it
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('login'))
    
    # For now, just show a simple message
    return f"<h1>Welcome, Admin! Your email is {session.get('user_email')}</h1>"


@app.route('/user/dashboard')
def user_dashboard():
    # Protect this route: any logged-in user can see it
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'danger')
        return redirect(url_for('login'))

    # For now, just show a simple message
    return f"<h1>Welcome, User! Your email is {session.get('user_email')}</h1>"









def create_admin_and_db():
    """Initializes the database and creates the default admin user."""
    with app.app_context():
        db.create_all()
        # FIX: Query by email instead of username
        admin = User.query.filter_by(email='admin@parkarage.com').first()
        if not admin:
            print("Creating admin user...")
            admin_user = User(
                # FIX: Use the email field
                email='admin@parkarage.com', 
                full_name='Admin User',
                is_admin=True,
                # Admin doesn't need a real address, so we use placeholders
                address='N/A', 
                pincode='000000'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")



if __name__ == '__main__':
    create_admin_and_db()
    app.run(debug=True)