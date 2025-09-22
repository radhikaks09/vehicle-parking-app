from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from model import db
from model.user import User
from model.parking import ParkingLot, ParkingSpot, Reservation
from datetime import datetime

user = Blueprint('user', __name__)

@user.route('/dashboard')
def dashboard():
    user_id = session.get('current_user_id')
    user = User.query.get_or_404(user_id)
    parking_lots = ParkingLot.query.all()
    return render_template("user/dashboard.html", parking_lots=parking_lots, role='user', current_user=user)

@user.route('/view-spots/<int:lot_id>')
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template("user/view_spots.html", lot=lot, spots=spots, role='user', current_user_id=session.get('current_user_id'))

@user.route('/reserve-spot/<int:lot_id>', methods=['GET', 'POST'])
def reserve_spot(lot_id):
    user_id = session.get('current_user_id')
    user = User.query.get_or_404(user_id)
    lot = ParkingLot.query.get_or_404(lot_id)

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, is_occupied=False).first()
    if not spot:
        flash("No available spots in this lot.", "error")
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')
        if not vehicle_number:
            flash("Vehicle number is required.", "error")
            return render_template('user/reserve.html', spot=spot, lot=lot)
        
        spot.is_occupied = True
        spot.vehicle_details = vehicle_number

        try:
            reservation = Reservation(
                user_id=user.id,
                spot_id=spot.id,
                start_time=datetime.utcnow(),
                is_active=True
            )
            db.session.add(reservation)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Error reserving spot", "error")
            return render_template('user/reserve.html', spot=spot, lot=lot, role='user')

        flash("Spot reserved successfully.", "success")
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/reserve.html', spot=spot, lot=lot, role='user')

@user.route('/release-spot/<int:lot_id>/<int:spot_number>', methods=['GET', 'POST'])
def release_spot(lot_id, spot_number):
    user_id = session.get('current_user_id')
    user = User.query.get_or_404(user_id)

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, spot_number=spot_number).first_or_404()
    reservation = Reservation.query.filter_by(user_id=user.id, spot_id=spot.id, is_active=True).first_or_404()

    end_time = datetime.utcnow()

    if request.method == 'POST':
        reservation.end_time = end_time
        reservation.is_active = False
        spot.is_occupied = False

        duration = (end_time - reservation.start_time).total_seconds() / 3600
        lot = ParkingLot.query.get(spot.lot_id)
        cost = round(duration * lot.price_per_hour, 2)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Error releasing spot", "error")
            return render_template('user/release.html', spot=spot, reservation=reservation, role='user')
        
        flash(f"Spot released. Duration: {duration:.2f} hours. Cost: ₹{cost}", "success")
        return redirect(url_for('user.dashboard'))
    
    duration = (datetime.utcnow() - reservation.start_time).total_seconds() / 3600
    lot = ParkingLot.query.get(spot.lot_id)
    cost = round(duration * lot.price_per_hour, 2)

    return render_template('user/release.html', spot=spot, reservation=reservation, end_time=end_time, cost=cost, role='user')

@user.route('/my-reservations', methods=['GET'])
def my_reservations():
    user_id = session.get('current_user_id')
    active_reservations = Reservation.query.filter_by(user_id=user_id, is_active=True).all()
    past_reservations = Reservation.query.filter_by(user_id=user_id, is_active=False).all()
    current_time = datetime.utcnow()
    return render_template('user/my_reservations.html', active_reservations=active_reservations, past_reservations=past_reservations, 
                           current_time=current_time, role='user')

@user.route('/booking-summary')
def booking_summary():
    user_id = session.get('current_user_id')
    active_reservations = Reservation.query.filter_by(user_id=user_id, is_active=True)
    past_reservations = Reservation.query.filter_by(user_id=user_id, is_active=False)
    total_reservations = active_reservations.count() + past_reservations.count()

    total_active_cost = 0
    for res in active_reservations:
        duration = (datetime.utcnow() - res.start_time).total_seconds() / 3600
        lot = ParkingLot.query.get(res.spot.lot_id)
        total_active_cost += duration * lot.price_per_hour

    total_past_cost = 0
    for res in past_reservations:
        if res.end_time:
            duration = (res.end_time - res.start_time).total_seconds() / 3600
            lot = ParkingLot.query.get(res.spot.lot_id)
            total_past_cost += duration * lot.price_per_hour


    return render_template('user/booking_summary.html', no_of_active_reservations=active_reservations.count(), 
                           no_of_past_reservations=past_reservations.count(), total_reservations=total_reservations, 
                           total_active_cost=total_active_cost, total_past_cost=total_past_cost, role='user')