from HospitalityManagement import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String , Boolean, ForeignKey, Float, DateTime, Enum
from HospitalityManagement import db
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin

# db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2


class Category(BaseModel):
    __tablename__ = 'category'

    name = Column(String(50), nullable=False)

    rooms = relationship('Room', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Room(BaseModel):
    __tablename__ = 'room'

    name = Column(String(50), nullable=False)
    description = Column(String(255))
    price = Column(Float, default=0)
    active = Column(Boolean, default=True)
    image = Column(String(100))
    created_date = Column(DateTime, default=datetime.now())
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)

    reservation_details = relationship('ReservationDetail', backref='room', lazy=True)
    rent_details = relationship('RentDetail', backref='room', lazy=True)
    comments = relationship('Comment', backref='room', lazy=True)

    def __str__(self):
        return self.name


class User(BaseModel, UserMixin):
    ___tablename__ = 'user'

    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    phone = Column(Integer)
    email = Column(String(100))
    avatar = Column(String(100))
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)

    reservation = relationship('Reservation', backref='user', lazy=True)
    receipt = relationship('ReceiptDetail', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Comment(BaseModel):
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    content = Column(String(255), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


class CustomerType(BaseModel):
    __tablename__ = 'customertype'

    name = Column(String(50), nullable=False)
    coefficient = Column(Float, default=1)
    customer = relationship('Customer', backref='customertype', lazy=True)
    def __str__(self):
        return str(self.id)

class Customer(BaseModel):
    __tablename__ = 'customer'

    name = Column(String(50), nullable=False)
    identity_card = Column(Integer, unique=True)
    address = Column(String(100))
    customertype_id = Column(Integer, ForeignKey('customertype.id'), nullable=False)
    rent_id = Column(Integer, ForeignKey('rentdetail.id'), nullable=False)

    def __str__(self):
        return self.name


class Reservation(BaseModel):
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    details = relationship('ReservationDetail', backref='reservation', lazy=True)


class ReservationDetail(db.Model):
    reservation_id = Column(Integer, ForeignKey(Reservation.id), nullable=False, primary_key=True)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)
    checkin_date = Column(DateTime, default=datetime.now())
    checkout_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)


class RentDetail(BaseModel):
    __tablename__ = 'rentdetail'

    reservation_id = Column(Integer, ForeignKey(ReservationDetail.reservation_id), nullable=True)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)
    quantity = Column(Integer, default=0)
    checkin_date = Column(DateTime, default=datetime.now())
    checkout_date = Column(DateTime, default=datetime.now())

    customer = relationship('Customer', backref='rentdetail', lazy=True)
    receipt = relationship('ReceiptDetail', backref='rentdetail', lazy=True)

    def __str__(self):
        return str(self.id)

class ReceiptDetail(db.Model):
    __tablename__ = 'receiptdetail'

    rent_id = Column(Integer, ForeignKey('rentdetail.id'), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, primary_key=True)
    created_date = Column(DateTime, default=datetime.now())
    unit_price = Column(Float, default=0)
    rate = Column(Float, default=0)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

