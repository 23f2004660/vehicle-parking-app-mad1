from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'User'
    User_id = db.Column(db.Integer, primary_key=True)
    User_name = db.Column(db.String(50),unique=True,nullable=False)
    Name = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(50), nullable=False)
    Contact = db.Column(db.String(20), nullable=True)
    reservations = db.relationship('ReserveParkingSpot', backref='user', lazy=True)

class Admin(db.Model):
    __tablename__ = 'Admin'
    Admin_Id = db.Column(db.Integer, primary_key=True)
    User_name = db.Column(db.String(50),unique=True,nullable=False)
    password = db.Column(db.String(50), nullable=False)
    Contact = db.Column(db.String(20), nullable=True)

class ParkingLot(db.Model):
    __tablename__ = 'Parking_Lot'
    Lot_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    prime_location_name = db.Column(db.String(50), nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    Spot_id = db.Column(db.Integer, primary_key=True)  # Primary key
    Lot_id = db.Column(db.Integer, db.ForeignKey('Parking_Lot.Lot_id'), nullable=False)
    status = db.Column(db.Boolean, default=True)

    reservations = db.relationship('ReserveParkingSpot', backref='spot', lazy=True)

class ReserveParkingSpot(db.Model):
    __tablename__ = 'reserve_parking_spot'
    Reserve_id = db.Column(db.Integer, primary_key=True)  # Primary key
    Lot_id = db.Column(db.Integer, db.ForeignKey('Parking_Lot.Lot_id'), nullable=False)  # Foreign key
    Spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.Spot_id'), nullable=False)  # Foreign key
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)  # Foreign key
    arrive_time = db.Column(db.DateTime, nullable=False)  # Required datetime
    leaving_time = db.Column(db.DateTime, nullable=False)  # Required datetime
    cost_per_time = db.Column(db.Float, nullable=False)  # Required decimal




