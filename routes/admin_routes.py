from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import User, db, ParkingLot, ParkingSpot, Reservation
from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))
    
    lots = ParkingLot.query.all()

    return render_template('admin/admin_dashboard.html', lots=lots)


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

        # after getting the data from the form, we create a new parking lot in the database
        new_lot = ParkingLot(
            name=name,
            address=address,
            pincode=pincode,
            capacity=capacity,
            price_per_hour=price_per_hour
        )

       
        for i in range(1, capacity + 1): #this creates the parking spots for the new lot
            spot = ParkingSpot(spot_number=i, status='A')
            new_lot.spots.append(spot)
        
        db.session.add(new_lot)
        db.session.commit()

        flash(f'Parking lot "{name}" created successfully with {capacity} spots.', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_lot.html')

@admin_bp.route('/admin/lot/<int:lot_id>')
def lot_details(lot_id):
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.options(
        joinedload(ParkingLot.spots).subqueryload(ParkingSpot.reservations)
    ).get(lot_id)
    
    if not lot:
        return "Lot not found", 404

    return render_template('admin/lot_details.html', lot=lot)

@admin_bp.route('/admin/users')
def view_users():
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))

    # get all users but not admins
    users = User.query.filter_by(is_admin=False).all()
    
    return render_template('admin/view_users.html', users=users)

@admin_bp.route('/admin/lot/delete/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))

    lot_to_delete = ParkingLot.query.get_or_404(lot_id)

    # check if any spot in the lot is occupied
    occupied_spots = any(spot.status == 'O' for spot in lot_to_delete.spots)
    if occupied_spots:
        flash('Cannot delete a lot with occupied spots. Please wait until it is empty.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    #if spots are free then we can delte
    db.session.delete(lot_to_delete)
    db.session.commit()
    flash(f'Parking lot "{lot_to_delete.name}" has been deleted.', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/lot/edit/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))

    lot_to_edit = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        # update fields
        lot_to_edit.name = request.form['name']
        lot_to_edit.address = request.form['address']
        lot_to_edit.pincode = request.form['pincode']
        lot_to_edit.price_per_hour = float(request.form['price_per_hour'])

        new_capacity = int(request.form['capacity'])
        current_capacity = lot_to_edit.capacity

        if new_capacity > current_capacity: #if new capacity is greater than current capacity then we add new spots
            for i in range(current_capacity + 1, new_capacity + 1):
                new_spot = ParkingSpot(spot_number=i, status='A')
                lot_to_edit.spots.append(new_spot)
            lot_to_edit.capacity = new_capacity

        elif new_capacity < current_capacity: #if new is less than current then we remove spots
            spots_to_remove_count = current_capacity - new_capacity
            
            # delete spots from the highest number if they available
            available_spots_to_delete = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.spot_number.desc()).limit(spots_to_remove_count).all()

            if len(available_spots_to_delete) < spots_to_remove_count:
                flash('Cannot decrease capacity by that much, too many spots are occupied.', 'danger')
                return redirect(url_for('admin.edit_lot', lot_id=lot_id))
            else:
                for spot in available_spots_to_delete:
                    db.session.delete(spot)
                lot_to_edit.capacity = new_capacity
        
        db.session.commit()
        flash(f'Successfully updated parking lot "{lot_to_edit.name}".', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/edit_lot.html', lot=lot_to_edit)

@admin_bp.route('/admin/search')
def search():
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))
    
    query = request.args.get('q', '')
    found_lots = []
    found_users = []

    if query:
        search_term = f"%{query}%" # Prepare the term for a 'like' search
        
        # Search ParkingLots by name, address, or pincode
        found_lots = ParkingLot.query.filter(
            or_(
                ParkingLot.name.ilike(search_term),
                ParkingLot.address.ilike(search_term),
                ParkingLot.pincode.ilike(search_term)
            )
        ).all()

        # Search Users by full_name or email
        found_users = User.query.filter_by(is_admin=False).filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        ).all()

    return render_template('admin/search_results.html', 
                           query=query, 
                           lots=found_lots, 
                           users=found_users)


@admin_bp.route('/admin/summary')
def summary_page():
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))

    # parking lot summary
    lots = ParkingLot.query.order_by(ParkingLot.name).all()
    lot_names = [lot.name for lot in lots]
    lot_capacities = [lot.capacity for lot in lots]

    available_spots = ParkingSpot.query.filter_by(status='A').count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    reserved_spots = ParkingSpot.query.filter_by(status='R').count()

    # revenue summary
    revenue_per_lot = []
    for lot in lots:
        # sum the total_cost for all completed reservations for this specific lot
        total = db.session.query(func.sum(Reservation.total_cost)).join(ParkingSpot).filter(
            ParkingSpot.lot_id == lot.id,
            Reservation.end_time.is_not(None)
        ).scalar() or 0.0
        revenue_per_lot.append(total)
    
    total_revenue = sum(revenue_per_lot)

    return render_template('admin/summary_charts.html',
                           lot_names=lot_names,
                           lot_capacities=lot_capacities,
                           available_spots=available_spots,
                           occupied_spots=occupied_spots,
                           reserved_spots=reserved_spots,
                           revenue_per_lot=revenue_per_lot,
                           total_revenue=total_revenue)

@admin_bp.route('/admin/records')
def all_records():
    if not session.get('is_admin'):
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('auth.login'))

    all_reservations = Reservation.query.filter(
        Reservation.end_time.is_not(None)
    ).order_by(Reservation.end_time.desc()).all()
    
    return render_template('admin/all_records.html', reservations=all_reservations)