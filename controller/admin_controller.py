from flask import Blueprint, render_template, request, redirect, url_for, flash
from model import db
from model.user import User
from model.parking import ParkingLot, ParkingSpot, Reservation
from datetime import datetime

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
def dashboard():
    parking_lots = ParkingLot.query.all()
    return render_template("admin/dashboard.html", parking_lots=parking_lots, role='admin', name='Admin')

@admin.route('/add-lot', methods=['GET', 'POST'])
def add_lot():
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        location = request.form.get('location')
        pincode = request.form.get('pincode')
        total_spots = int(request.form.get('total_spots'))
        price_per_hour = float(request.form.get('price_per_hour'))

        try:
            new_lot = ParkingLot(
                id=id,
                name=name,
                location=location,
                pincode=pincode,
                total_spots=total_spots,
                price_per_hour=price_per_hour
            )
            db.session.add(new_lot)
            db.session.flush()
            
            for i in range(1, total_spots + 1):
                spot = ParkingSpot(lot_id=id, spot_number=i)
                db.session.add(spot)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Error adding parking lot", "error")
            return render_template("admin/add_lot.html", role='admin', name='Admin')
        
        flash("Parking lot added successfully!", "success")
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/add_lot.html', role='admin', name='Admin')

@admin.route('/edit-lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.name = request.form.get('name')
        lot.location = request.form.get('location')
        lot.pincode = request.form.get('pincode')
        lot.total_spots = int(request.form.get('total_spots'))
        lot.price_per_hour = float(request.form.get('price_per_hour'))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating parking lot", "error")

        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_lot.html', lot=lot, role='admin', name='Admin')

@admin.route('/delete-lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    occupied_spots = any(spot.is_occupied for spot in lot.spots)
    if occupied_spots:
        flash("Cannot delete parking lot with occupied spots!", "error")
        return redirect(url_for('admin.dashboard'))
    
    try:
        db.session.delete(lot)
        db.session.commit()
        flash("Parking lot deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting parking lot", "error")
    
    return redirect(url_for('admin.dashboard'))

@admin.route('/lot/<int:lot_id>/spots', methods=['GET'])
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('admin/view_spots.html', lot=lot, spots=spots, now=datetime.utcnow(), role='admin', name='Admin')

@admin.route('/view-users')
def view_users():
    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin/view_users.html', users=users, role='admin', name='Admin')

@admin.route('/parking-summary')
def parking_summary():
    total_users = User.query.count()
    total_lots = ParkingLot.query.count()
    
    completed_reservations = Reservation.query.filter(Reservation.is_active == False).all()
    total_revenue = 0
    for res in completed_reservations:
        if res.end_time:
            duration = (res.end_time - res.start_time).total_seconds() / 3600
            lot = ParkingLot.query.get(res.spot.lot_id)
            total_revenue += duration * lot.price_per_hour

    return render_template('admin/parking_summary.html', total_users=total_users, total_lots=total_lots, 
                           total_revenue=round(total_revenue, 2), role='admin')