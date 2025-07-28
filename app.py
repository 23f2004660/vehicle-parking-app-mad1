from flask import Flask
from models.database import db, User
# Import both blueprints
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
from zoneinfo import ZoneInfo
from datetime import datetime

app = Flask(__name__)

# --- App Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-super-secret-key'

def to_ist(utc_dt):
    if utc_dt is None:
        return ""
    # Convert naive datetime to UTC-aware datetime
    utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
    # Convert to India Standard Time
    return utc_dt.astimezone(ZoneInfo("Asia/Kolkata"))

# Register the function as a filter
app.jinja_env.filters['to_ist'] = to_ist

# Initialize database
db.init_app(app)

# Register both blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

# --- Helper Functions ---
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

# --- Main Execution Block ---
if __name__ == '__main__':
    create_admin_and_db()
    app.run(debug=True)