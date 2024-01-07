import math
from flask import render_template, request, redirect, url_for, session, jsonify
from HospitalityManagement import app, login
import utils
import cloudinary.uploader
from flask_login import login_user, logout_user, login_required
from HospitalityManagement.admin import *
from flask_babel import Babel
from HospitalityManagement.models import UserRole


@app.route("/")
def home():
    cate_id = request.args.get('category_id')
    kw = request.args.get('keyword')
    rooms = utils.load_rooms(cate_id=cate_id, kw=kw)
    # counter = utils.count_rooms()

    return render_template("index.html",
                           rooms=rooms)


@app.context_processor
def general_info(): #thông tin chung cần hiển thị mọi trang
    return {
        'categories': utils.load_categories(),  #ds danh mục
        'cart_stats': utils.count_cart(session.get('cart')),  # số lượng sp trong giỏ hàng
        'customertype_id': utils.load_customer_type(),
        'reservations': utils.load_reservation_detail()
    }


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/admin/login', methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route("/register", methods=['get', 'post'])
def register():
    error_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        phone = request.form.get('phone')
        email = request.form.get('email')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(name=name, username=username, password=password,
                               phone=phone, email=email, avatar=avatar_path)

                return redirect(url_for('user_signin'))
            else:
                error_msg = "Mật khẩu xác thực không khớp!!!"
        except Exception as ex:
            error_msg = "Hệ thống đang có lỗi" + str(ex)

    return render_template("register.html", error_msg=error_msg)


@app.route('/user-login', methods=['POST', 'GET'])
def user_signin():
    error_msg = ""

    if request.method.__eq__('POST'):
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = utils.check_login(username=username, password=password, role=UserRole.USER)
            user_admin = utils.check_login(username=username, password=password, role=UserRole.ADMIN)

            if user:
                login_user(user=user)

                if 'room_id' in request.args:
                    return redirect(url_for(request.args.get('next', 'home'), room_id=request.args['room_id']))

                return redirect(url_for(request.args.get('next', 'home')))

            elif user_admin:
                return redirect(url_for(request.args.get('next', 'rooms_list')))

            else:
                error_msg = "Tài khoản hoặc mật khẩu chưa chính xác!!!"

        except Exception as ex:
            error_msg = "Hệ thống đang có lỗi" + str(ex)

    return render_template("login.html", error_msg=error_msg)


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route("/rooms")
def rooms_list():
    cate_id = request.args.get("category_id")
    kw = request.args.get("keyword")
    from_price = request.args.get("from_price")
    to_price = request.args.get("to_price")

    rooms = utils.load_rooms(cate_id=cate_id, kw=kw,
                             from_price=from_price,
                             to_price=to_price)

    return render_template("admin/rooms.html",
                           rooms=rooms)


@app.route("/rooms/<int:room_id>")
def room_detail(room_id):     #xem chi tiết sp
    room = utils.get_room_by_id(room_id)
    comments = utils.get_comments(room_id=room_id,
                                  page=int(request.args.get('page', 1)))

    return render_template("room_detail.html",
                           comments=comments,
                           room=room,
                           pages=math.ceil(utils.count_comment(room_id=room_id)/app.config['COMMENT_SIZE']))


@app.route('/api/comments', methods=['post'])
@login_required     #bắt buộc đăng nhập mới được thực hiện
def add_comment():
    data = request.json
    content = data.get('content')
    room_id = data.get('room_id')

    try:
        c = utils.add_comment(content=content, room_id=room_id)
    except:
        return {'status': 404, 'err_msg': 'Chương trình đang bị lỗi!!!'}

    return {'status': 201, 'comment': {
        'id': c.id,
        'content': c.content,
        'created_date': c.created_date,
        'user': {
            'username': current_user.username,
            'avatar': current_user.avatar
        }
    }}


@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')
    checkinDate = data.get('checkinDate')
    checkoutDate = data.get('checkoutDate')

    cart = session.get('cart')
    if not cart:    #kiểm tra có giỏ hàng chưa
        cart = {}

    if id in cart:  #kiểm tra xem sp đó có trong giỏ hàng chưa
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1,
            'checkin_date': checkinDate,
            'checkout_date': checkoutDate
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html',
                           stats=utils.count_cart(session.get('cart')))


@app.route('/api/update-cart', methods=['put']) #cập nhật thì dùng put
def update_cart():  #cập nhật số lượng sp trong giỏ
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')
    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/delete-cart/<room_id>', methods=['delete'])
def delete_cart(room_id):    #xóa sp trong giỏ
    cart = session.get('cart')

    if cart and room_id in cart:
        del cart[room_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/reservation', methods=['post'])
@login_required
def reservation():
    try:
        utils.add_reservation(session.get('cart'))
        del session['cart']  #xóa tất cả sp trong giỏ sau khi thanh toán xong

    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


#Thuê phòng
@app.route('/rent_detail', methods=['post', 'get'])
def rent_detail():
    err_msg = ""
    rooms = utils.load_roomname()

    if request.method.__eq__('POST'):
        checkin = request.form.get('checkin_date')
        checkout = request.form.get('checkout_date')
        quantity = request.form.get('quantity')
        room_id = request.form.get('room_id')
        try:
            utils.add_rent_detail(room_id=room_id, checkin_date=checkin,
                                  checkout_date=checkout, quantity=quantity)
            utils.inactive_room(room_id)
            return redirect(url_for('savecustomer'))
        except Exception as ex:
            err_msg = 'LỖI - ' + str(ex)
    return render_template('rent_detail.html', rooms=rooms, err_msg=err_msg)


@app.route('/savecustomer', methods=['post', 'get'])
def savecustomer():
    max = 0
    err_msg = ""
    reservations = utils.load_reservation_detail()
    rooms = utils.load_roomname()
    rent = utils.load_rent_detail()
    for i in rent:
        if i.id > max:
            max = i.id
    r = utils.get_rentdetail_by_id(max)
    room_getname = utils.get_room_by_id(r.room_id)
    if request.method.__eq__('POST'):
        name = request.form.get('cname')
        identity_card = request.form.get('identity_card')
        customertype_id = request.form.get('customertype_id')
        address = request.form.get('address')

        name2 = request.form.get('cname2')
        identity_card2 = request.form.get('identity_card2')
        customertype_id2 = request.form.get('customertype_id2')
        address2 = request.form.get('address2')

        name3 = request.form.get('cname3')
        identity_card3 = request.form.get('identity_card3')
        customertype_id3 = request.form.get('customertype_id3')
        address3 = request.form.get('address3')

        try:
            if utils.check_add_customer(r.id) == False:
                err_msg = "Đã lưu đủ số lượng khách hàng trên phiếu thuê phòng!!!"
            else:
                utils.add_customer(name=name, rent_id=r.id, identity_card=identity_card,
                                   customertype_id=customertype_id, address=address)
                if r.quantity == 2:
                    utils.add_customer(name=name2, rent_id=r.id, identity_card=identity_card2,
                                       customertype_id=customertype_id2, address=address2)
                if r.quantity == 3:
                    utils.add_customer(name=name2, rent_id=r.id, identity_card=identity_card2,
                                       customertype_id=customertype_id2, address=address2)
                    utils.add_customer(name=name3, rent_id=r.id, identity_card=identity_card3,
                                       customertype_id=customertype_id3, address=address3)
                return redirect(url_for('rooms_list'))
        except Exception as ex:
            err_msg = 'LỖI - ' + str(ex)
    return render_template('savecustomer.html', rooms=rooms, reservations=reservations, rent=rent, r=r, err_msg=err_msg, room_getname=room_getname)


@app.route('/reservation', methods=['post', 'get'])
def all_reservation():
    reservations = utils.load_reservation_detail()
    room = utils.load_room2()
    return render_template('reservation.html', reservations=reservations, room=room)


@app.route("/rentdetail/<int:roomid>", methods=['post', 'get'])
def reservation_to_rent(roomid):
    user = 0
    re_id = 0
    err_msg = ""
    customers = utils.load_customer()
    reservations = utils.load_reservation_detail()
    for r in reservations:
        if roomid == r.room_id:
            re_id = r.reservation_id
    reservation_detail = utils.get_reservationdetail_by_id(re_id, roomid)
    room = utils.get_room_by_id(reservation_detail.room_id)
    timein = str(reservation_detail.checkin_date)
    timeout = str(reservation_detail.checkout_date)
    t_in = timein.split()
    t_out = timeout.split()
    time_checkin = t_in[0] + "T" + t_in[1]
    time_checkout = t_out[0] + "T" + t_out[1]

    if request.method.__eq__('POST'):
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        quantity = request.form.get('quantity')
        try:
            utils.add_rent_detail(reservation_id=reservation_detail.reservation_id, room_id=roomid,
                                  checkin_date=checkin, checkout_date=checkout, quantity=quantity)
            utils.inactive_reservationdetail(re_id, roomid)
            utils.inactive_room(roomid)

            return redirect(url_for('savecustomer'))
        except Exception as ex:
            err_msg = 'LỖI - ' + str(ex)

    return render_template('reservation_to_rent.html', reservation_detail=reservation_detail, customers=customers, err_msg=err_msg,
                           reservations=reservations, time_checkin=time_checkin, time_checkout=time_checkout, room=room, roomid=roomid)


#Thanh toán
@app.route('/payment')
@login_required
def payment():
    id = request.args.get('id')
    rents = utils.load_rentdetails(id=id)
    rooms = utils.load_room2()
    reservations = utils.load_reservationdetails()
    users = utils.load_user()
    reservation = utils.load_reservation()

    return render_template('payment.html', rentdetails=rents, rooms=rooms, reservationdetails=reservations,
                           users=users, reservation=reservation)


@app.route('/payment/<int:rent_id>', methods=['post', 'get'])
@login_required
def paydetail(rent_id):
    err = ""
    unit_price = 1
    rate = 1
    rent = utils.get_rent_by_id(rent_id)
    rents = utils.load_rentdetails()
    rooms = utils.load_room2()
    reservations = utils.load_reservationdetails()
    users = utils.load_user()
    reservation = utils.load_reservation()
    customers = utils.load_customer()
    type = utils.load_customertype()
    for r in rooms:
        for d in rents:
            for c in customers:
                if rent.id == c.rent_id:
                    for t in type:
                        if rent.id == c.rent_id and t.id == c.customertype_id and d.room_id == r.id:
                            if d.quantity == 2:
                                unit_price = r.price * t.coefficient
                            else:
                                unit_price = r.price * t.coefficient * 1.25
                        rate = t.coefficient
    try:
        utils.add_receipt(unit_price=unit_price, rent_id=rent.id, rate=rate)
        utils.inactive_rent(rent.id)

    except Exception as ex:
            err = 'LỖI - ' + str(ex)

    return render_template('paydetail.html', rentdetails=rents, rooms=rooms,  customers=customers, err=err, type=type,
                           reservationdetails=reservations, users=users, reservation=reservation,
                           rent=rent, unit_price=unit_price, rate=rate)



if __name__ == '__main__':
    from HospitalityManagement.admin import *

    app.run(debug=True)