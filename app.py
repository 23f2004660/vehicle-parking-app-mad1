#app.py
from flask import Flask
from models.database import db, User, ParkingLot, ParkingSpot, Reservation

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-super-secret-key'

db.init_app(app) #initializing db

def create_admin_and_db():
    """Initializing the database and creating the default admin user."""
    with app.app_context():
        db.create_all()
        # checking if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creating admin user...")
            admin_user = User(
                username='admin', 
                full_name='Admin User',
                is_admin=True
            )
            admin_user.set_password('admin123') # setting a default password
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

# this block will run only when you execute `python app.py` directly
if __name__ == '__main__':
    create_admin_and_db() # this creates your DB and admin on first run
    app.run(debug=True)
