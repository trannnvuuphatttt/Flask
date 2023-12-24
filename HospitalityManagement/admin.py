from HospitalityManagement import db, app, utils
from HospitalityManagement.models import Category, Room, UserRole, Customer, User, CustomerType
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin, AdminIndexView
from flask_login import logout_user, current_user, login_user
from flask import redirect, request
from datetime import datetime


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class BasicView(AuthenticatedModelView):
    column_display_pk = True  # hiển thị trường khóa chính id
    can_view_details = True  # xem chi tiết

    can_export = True  # xuất file

    edit_modal = True  # bật modal chỉnh sửa
    details_modal = True #bật xem chi tiết
    create_modal = True #bật modal tạo

    column_filters = ['name']  # bật bộ lọc


class RoomView(BasicView):
    column_exclude_list = ['image', 'active', 'created_date']  # ẩn cột
    column_filters = ['name', 'price']  # bật bộ lọc
    column_searchable_list = ['name', 'description']  # bật box tìm kiếm
    column_sortable_list = ['id', 'name', 'price']  # sắp xếp
    column_labels = {
        'id': 'Mã phòng',
        'name': 'Tên phòng',
        'description': 'Mô tả',
        'price': 'Đơn giá',
        'category': 'Loại phòng',
        'active': 'Tình trạng',
        'created_date': 'Ngày tạo',
        'image': 'Ảnh'
    }


class UserView(BasicView):
    column_display_pk = False  # ẩn trường khóa chính id
    column_exclude_list = ['password', 'avatar', 'active'] #ẩn cột
    column_labels = {
        'id': 'Mã',
        'name': 'Tên người dùng',
        'username': 'Tên tài khoản',
        'password': 'Mật khẩu',
        'phone': 'Số điện thoại',
        'email': 'Địa chỉ mail',
        'active': 'Tình trạng',
        'joined_date': 'Ngày tạo',
        'avatar': 'Ảnh đại diện',
        'user_role': 'Vai trò'
    }


class CustomerTypeView(BasicView):
    can_view_details = False
    can_create = True
    column_labels = {
        'id': 'Mã loại KH',
        'name': 'Tên loại khách hàng',
        'coefficient': 'Hệ số'
    }


class CustomerView(BasicView):
    can_create = False  #tắt chức năng tạo
    can_delete = False
    column_searchable_list = ['name', 'identity_card']  # bật box tìm kiếm
    column_sortable_list = ['name']  # sắp xếp
    column_labels = {
        'id': 'Mã KH',
        'name': 'Họ tên khách hàng',
        'address': 'Địa chỉ',
        'identity_card': 'Số CMND/CCCD',
        'customertype': 'Loại KH',
        'rentdetail': 'Mã phiếu thuê phòng'
    }


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class LogoutView(AuthenticatedBaseView):  # đăng xuất
    @expose('/')
    def index(self):
        logout_user()

        return redirect('/admin')


class StatsView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
       # kw = request.args.get('kw')
       year = request.args.get('year', datetime.now().year)
       month = request.args.get('month', datetime.now().month)

       return self.render('admin/stats.html',
                          month_stats=utils.room_month_stats(month=month),
                          stats1=utils.density_of_room_use_stats(month=month),
                          total=utils.total_revenue(month=month))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html',
                           stats=utils.category_stats())


admin = Admin(app=app, name='QUAN TRI KHACH SAN',
              template_mode='bootstrap4',
              index_view=MyAdminIndexView())


admin.add_view(AuthenticatedModelView(Category, db.session, name='Loại phòng'))
admin.add_view(RoomView(Room, db.session, name='Phòng'))
admin.add_view(CustomerTypeView(CustomerType, db.session, name='Loại khách'))
admin.add_view(CustomerView(Customer, db.session, name='Khách hàng'))
admin.add_view(UserView(User, db.session, name='Người dùng'))
admin.add_view(StatsView(name='Thống kê'))

admin.add_view(LogoutView(name="Đăng xuất"))