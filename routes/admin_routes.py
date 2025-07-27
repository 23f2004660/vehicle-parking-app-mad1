from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import db, ParkingLot, ParkingSpot

# Create a blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    # Protect this route: only admins should see it
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))
    
    #get all parking lots
    lots = ParkingLot.query.all()

    return render_template('admin_dashboard.html', lots=lots)

@admin_bp.route('/admin/add_lot', methods=['GET', 'POST'])
def add_lot_page():
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        pincode = request.form['pincode']
        capacity = int(request.form['capacity'])
        price_per_hour = float(request.form['price_per_hour'])

        # Create the new ParkingLot object in the database
        new_lot = ParkingLot(
            name=name,
            address=address,
            pincode=pincode,
            capacity=capacity,
            price_per_hour=price_per_hour
        )

       
        for i in range(1, capacity + 1):
            spot = ParkingSpot(spot_number=i, status='A')
            new_lot.spots.append(spot)
        
        db.session.add(new_lot)
        db.session.commit()

        flash(f'Parking lot "{name}" created successfully with {capacity} spots.', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    # For a GET request, just show the form
    return render_template('add_lot.html')