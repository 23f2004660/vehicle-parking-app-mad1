#models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

#initializing db
db = SQLAlchemy()

#user model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # Using email as the unique identifier is standard practice
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    # Your new fields
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade="all, delete-orphan")

    # handling password hashing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete-orphan")

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False) # 'A' for Available, 'O' for Occupied

    reservation = db.relationship('Reservation', backref='spot', uselist=False, cascade="all, delete-orphan")

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True) 
    total_cost = db.Column(db.Float, nullable=True)