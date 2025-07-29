from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.database import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
import math



user_bp = Blueprint('user', __name__)

@user_bp.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'danger')
        return redirect(url_for('auth.login'))
    

    active_reservations = Reservation.query.filter(
        Reservation.user_id == session['user_id'], 
        Reservation.end_time.is_(None) #because if endtime is not none then the reservation is over
    ).all()
    

    lots = ParkingLot.query.all()
    
    return render_template('user/user_dashboard.html', lots=lots, active_reservations=active_reservations)

@user_bp.route('/user/book/<int:lot_id>', methods=['POST'])
def book_spot(lot_id):

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first() #this finds the first available spot in the lot

    if available_spot:
        available_spot.status = 'R'
        
        new_reservation = Reservation(
            user_id=session['user_id'],
            spot_id=available_spot.id
        )
        db.session.add(new_reservation)
        db.session.commit()
        flash(f'Successfully reserved Spot #{available_spot.spot_number}!', 'success')
    else:
        flash('Sorry, no spots are available in this lot.', 'danger')

    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/user/occupy/<int:reservation_id>', methods=['POST'])
def occupy_spot(reservation_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        return redirect(url_for('user.user_dashboard'))

    # Set the start time and change status to Occupied
    reservation.start_time = datetime.utcnow()
    reservation.spot.status = 'O'
    db.session.commit()

    flash(f'Parking session started for Spot #{reservation.spot.spot_number}.', 'success')
    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/user/release/<int:reservation_id>', methods=['POST'])
def release_spot(reservation_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id'] or reservation.start_time is None:
        return redirect(url_for('user.user_dashboard'))

    
    reservation.end_time = datetime.utcnow()
    duration_minutes = (reservation.end_time - reservation.start_time).total_seconds() / 60
    
    if duration_minutes <= 30:
        blocks_to_charge = 1
    else:
        blocks_to_charge = math.ceil(duration_minutes / 30)

    hours_to_charge = blocks_to_charge * 0.5
    price_per_hour = reservation.spot.lot.price_per_hour
    total_cost = hours_to_charge * price_per_hour
    
    reservation.total_cost = total_cost
    reservation.spot.status = 'A'
    db.session.commit()

    flash(f'Spot released. You parked for {duration_minutes:.0f} minutes. Total cost: ₹{total_cost:.2f}', 'success')
    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/user/history')
def parking_history():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'danger')
        return redirect(url_for('auth.login'))

    # all completed reservations for the user
    completed_reservations = Reservation.query.filter(
        Reservation.user_id == session['user_id'],
        Reservation.end_time.is_not(None)
    ).order_by(Reservation.end_time.desc()).all()
    
    return render_template('user/history.html', reservations=completed_reservations)