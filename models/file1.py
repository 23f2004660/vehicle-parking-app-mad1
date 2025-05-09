from app import db,User,Admin,ParkingLot,ParkingSpot,ReserveParkingSpot,app
from datetime import datetime

with app.app_context():
    db.create_all()
# Create test users and admin
    user1 = User(User_name="john_doe", Name="John Doe", password="1234", Contact="9876543210")
    admin1 = Admin(User_name="admin1", password="admin123", Contact="1234567890")

    # Create a parking lot
    lot1 = ParkingLot(address="123 Main Street", pincode="400001", prime_location_name="Downtown", max_spots=50, price=20.0)

    # Create a parking spot in that lot
    spot1 = ParkingSpot(Lot_id=1, status=True)

    reservation1 = ReserveParkingSpot(
        Lot_id=1,
        Spot_id=1,
        User_id=1,
        arrive_time=datetime(2025, 5, 9, 10, 0),
        leaving_time=datetime(2025, 5, 9, 12, 0),
        cost_per_time=20.0
    )


    print("Data inserted successfully!!")





