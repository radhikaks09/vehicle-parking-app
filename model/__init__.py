from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from model.user import User
from model.parking import ParkingLot, ParkingSpot, Reservation