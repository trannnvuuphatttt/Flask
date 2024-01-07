import json, os
from HospitalityManagement import app, db
import datetime
from HospitalityManagement.models import Category, Room, UserRole, User, Comment, Reservation, ReservationDetail, RentDetail, ReceiptDetail, Customer, CustomerType
import hashlib
from HospitalityManagement.models import User
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.sql import extract


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username.strip(),
                password=password,
                phone=kwargs.get('phone'),
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password, role=UserRole.USER):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()


def category_stats():  # thống kê theo loại phòng
    return db.session.query(Category.id, Category.name, func.count(Room.id)) \
        .join(Room, Category.id.__eq__(Room.category_id), isouter=True) \
        .group_by(Category.id, Category.name).all()


def load_categories():
    return Category.query.all()


def load_rooms(cate_id=None, kw=None, from_price=None, to_price=None):
    rooms = Room.query.filter(Room.active.__eq__(True))

    if cate_id:
        rooms = rooms.filter(Room.category_id.__eq__(cate_id))

    if kw:
        rooms = rooms.filter(Room.name.contains(kw))

    if from_price:
        rooms = rooms.filter(Room.price.__ge__(from_price))

    if to_price:
        rooms = rooms.filter(Room.price.__le__(to_price))

    return rooms.all()


def count_rooms():
    return Room.query.filter(Room.active.__eq__(True)).count()


def get_room_by_id(room_id):
    return Room.query.get(room_id)


def add_comment(content, room_id):
    c = Comment(content=content, room_id=room_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(room_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return Comment.query.filter(Comment.room_id.__eq__(room_id)) \
        .order_by(-Comment.id).slice(start, end).all()


def count_comment(room_id):  # đếm số cmt của sp
    return Comment.query.filter(Comment.room_id.__eq__(room_id)).count()


def count_cart(cart):  # đếm số sản phẩm có trong giỏ
    total_quantity, total_amount = 0, 0  # amount~ tổng tiền trong giỏ

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def add_reservation(cart):
    if cart:
        reservation = Reservation(user=current_user)
        db.session.add(reservation)

        for c in cart.values():
            d = ReservationDetail(reservation=reservation,
                                  room_id=c['id'],
                                  quantity=c['quantity'],
                                  unit_price=c['price'],
                                  checkin_date=c['checkin_date'],
                                  checkout_date=c['checkout_date'])

            db.session.add(d)

        db.session.commit()


# Thuê phòng
def load_customer_type():
    return CustomerType.query.all()


def load_reservation_detail():
    re = ReservationDetail.query.filter(ReservationDetail.active.__eq__(True))
    return re.all()


def inactive_reservationdetail(id, roomid):
    r = get_reservationdetail_by_id(id, roomid)
    r.active = False
    db.session.commit()


def load_roomname():
    rooms = Room.query.filter(Room.active.__eq__(True))
    return rooms.all()


def load_room2():
    return Room.query.all()


# def load_customer():
#     return Customer.query.all()


def load_rent_detail():
    return RentDetail.query.all()


def add_rent_detail(room_id, checkin_date, checkout_date, **kwargs):
    rent = RentDetail(reservation_id=kwargs.get('reservation_id'),
                      room_id=room_id,
                      checkin_date=checkin_date,
                      checkout_date=checkout_date,
                      quantity=kwargs.get('quantity'),
                      created_date=kwargs.get('created_date'))
    db.session.add(rent)
    db.session.commit()


def add_customer(name, identity_card, customertype_id, rent_id, **kwargs):
    cus = Customer(name=name,
                   rent_id=rent_id,
                   identity_card=identity_card,
                   customertype_id=customertype_id,
                   address=kwargs.get('address'))
    db.session.add(cus)
    db.session.commit()


def inactive_room(room_id):
    r = get_room_by_id(room_id)
    r.active = False
    db.session.commit()


def get_rentdetail_by_id(id):
    return RentDetail.query.get(id)


def get_customer_in_rentdetail(idrent):
    customer = RentDetail.query.filter(RentDetail.id.__eq__(idrent))
    return customer.all()


def get_reservationdetail_by_id(id, roomid):
    reser = ReservationDetail.query.all()
    for r in reser:
        if r.room_id == roomid and r.reservation_id == id:
            return r


def check_add_customer(rentid):
    rent = get_rentdetail_by_id(rentid)
    quantity = Customer.query.filter(Customer.rent_id.__eq__(rentid)).count()
    if quantity < rent.quantity:
        return True
    else:
        return False


def delete_reservation(id):
    re = ReservationDetail.query.filter(ReservationDetail.reservation_id.__eq__(id))
    db.session.delete(re)
    db.session.commit()


# -----------------------------Thanh toán
def load_rentdetails(id=None):
    rent = RentDetail.query.filter(Room.active == True)

    if id:
        rent = rent.filter(RentDetail.id.__eq__(id))
    return rent.all()


def load_user():
    return User.query.all()


def load_reservation():
    return Reservation.query.all()


def get_rent_by_id(rent_id):
    return RentDetail.query.get(rent_id)


def load_reservationdetails():
    return ReservationDetail.query.all()


def load_customer():
    return Customer.query.all()


def load_customertype():
    return CustomerType.query.all()


def add_receipt(unit_price, rent_id, rate):
    receipt = ReceiptDetail(rent_id=rent_id,
                            user=current_user,
                            unit_price=unit_price,
                            rate=rate)
    db.session.add(receipt)
    db.session.commit()


def inactive_rent(rent_id):
    r = get_rent_by_id(rent_id)
    r.active = False
    db.session.commit()


# Thống kê
def density_of_room_use_stats(month):  # Thống kê mật độ sử dụng theo tháng
    p = db.session.query(Room.id, Room.name,
                         (extract('day', RentDetail.checkout_date) - extract('day', RentDetail.checkin_date)) + 1) \
        .join(RentDetail, RentDetail.room_id.__eq__(Room.id), isouter=True) \
        .filter(extract('month', RentDetail.created_date) == month) \
        .group_by(Room.id, Room.name,
                  (extract('day', RentDetail.checkout_date) - extract('day', RentDetail.checkin_date)) + 1) \
        .order_by(Room.id)

    return p.all()


def room_month_stats(month):  # Thống kê doanh thu theo tháng
    return db.session.query(Room.category_id, func.sum(ReceiptDetail.unit_price), func.count(RentDetail.id)) \
        .join(RentDetail, RentDetail.room_id.__eq__(Room.id)) \
        .filter(extract('month', RentDetail.created_date) == month) \
        .group_by(Room.category_id).all()


def total_revenue(month):  # tổng doanh thu
    return db.session.query(func.sum(ReceiptDetail.unit_price)).filter(
        extract('month', RentDetail.created_date) == month).all()
