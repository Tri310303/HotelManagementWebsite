from datetime import datetime
from app import app, db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import Relationship
from enum import Enum as CommonEnum
from flask_login import UserMixin

from flask import url_for


class UserRole(CommonEnum):
    ADMIN = 1
    RECEPTIONIST = 2
    CUSTOMER = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)


class User(BaseModel, UserMixin):
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(200), default='https://res.cloudinary.com/dg1zsnywc/image/upload/v1715800302/avt_zrf6wj.jpg')
    gender = Column(Boolean, default=True)  # True = 1 is 'Man'


class Administrator(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)


class Receptionist(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    reservations = Relationship('Reservation', backref='receptionist', lazy=True)
    room_rentals = Relationship('RoomRental', backref='receptionist', lazy=True)


class CustomerType(BaseModel):
    type = Column(String(50), default='DOMESTIC')
    customers = Relationship('Customer', backref='customer_type', lazy=True)

    def __str__(self):
        return self.type


class Customer(db.Model):
    id = Column(Integer, ForeignKey(User.id), unique=True)  # khóa ngoại tham chiếu đến User
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    identification = Column(String(15), unique=True)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)
    reservations = Relationship('Reservation', backref='customer', lazy=True)
    comments = Relationship('Comment', backref='customer', lazy=True)
    reservation_details = Relationship('ReservationDetail', backref='customer', lazy=True)

    def __str__(self):
        return self.name


class RoomType(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    rooms = Relationship('Room', backref='room_type', lazy=True)

    def __str__(self):
        return self.name


class Room(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    image = Column(String(500), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    reservations = Relationship('Reservation', backref='room', lazy=True)
    room_rentals = Relationship('RoomRental', backref='room', lazy=True)
    comments = Relationship('Comment', backref='room', lazy=True)

    def __str__(self):
        return self.name


class Reservation(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.customer_id))
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id))
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    is_checkin = Column(Boolean, default=False)
    deposit = Column(Float, nullable=False)
    reservation_details = Relationship('ReservationDetail', backref='reservation', lazy=True)


class ReservationDetail(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.customer_id), primary_key=True)
    reservation_id = Column(Integer, ForeignKey(Reservation.id), primary_key=True)


class RoomRental(BaseModel):
    # customer_id = Column(Integer, ForeignKey(Customer.customer_id))
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id))  # null if is_received_room == True
    reservation_id = Column(Integer, ForeignKey(Reservation.id))  # null if is_received_room == False
    checkin_date = Column(DateTime, default=datetime.now())
    checkout_date = Column(DateTime)
    deposit = Column(Float)
    is_paid = Column(Boolean, default=False)
    room_rental_details = Relationship('RoomRentalDetail', backref='room_rental', lazy=True)

    receipt = Relationship('Receipt', uselist=False, back_populates='room_rental')


class RoomRentalDetail(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.customer_id), primary_key=True)
    room_rental_id = Column(Integer, ForeignKey(RoomRental.id), primary_key=True)


class Receipt(BaseModel):
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id), nullable=False)
    rental_room_id = Column(Integer, ForeignKey(RoomRental.id), nullable=False)
    room_rental = Relationship('RoomRental', back_populates='receipt')
    total_price = Column(Float, nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())


class Comment(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    content = Column(String(1000), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)
    created_date = Column(DateTime, default=datetime.now())


class RoomRegulation(BaseModel):
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False, primary_key=True)
    admin_id = Column(Integer, ForeignKey(Administrator.id), nullable=False)
    room_quantity = Column(Integer, default=10)
    capacity = Column(Integer, default=2)
    price = Column(Float, default=100000)
    surcharge = Column(Float, default=0.25)
    deposit_rate = Column(Float, default=0.3)
    distance = Column(Integer, nullable=False, default=28)


class CustomerTypeRegulation(BaseModel):
    rate = Column(Float, default=1.0, nullable=False)
    admin_id = Column(Integer, ForeignKey(Administrator.id), nullable=False)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False, primary_key=True)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        rt1 = RoomType(name='Phòng Đơn')
        rt2 = RoomType(name='Phòng Đôi')
        rt3 = RoomType(name='Giường Đôi')
        db.session.add_all([rt1, rt2, rt3])
        db.session.commit()

        r1 = Room(name='D21', room_type_id=2, image='images/phong1.jpg')
        r2 = Room(name='D22', room_type_id=3, image='images/phong2.jpg')
        r3 = Room(name='D23', room_type_id=2, image='images/phong3.jpg')
        r4 = Room(name='D24', room_type_id=1, image='images/phong4.jpg')
        r5 = Room(name='D25', room_type_id=3, image='images/phong5.jpg')
        r6 = Room(name='D26', room_type_id=3, image='images/phong6.jpg')
        db.session.add_all([r1, r2, r3, r4, r5, r6])
        db.session.commit()

        ######################################################

        import hashlib

        user1 = User(
            role=UserRole.ADMIN,
            username='tri123',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            avatar='https://res.cloudinary.com/dg1zsnywc/image/upload/v1709066108/z5198999749329_e5e37f56d9aedfe2caca17ebe75fba7d_db43tu.jpg',
            email='ductai4201@gmail.com',
            phone='0375290878')
        user2 = User(
            role=UserRole.CUSTOMER,
            username='thientu',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            avatar='https://res.cloudinary.com/dg1zsnywc/image/upload/v1715784258/z5198997831482_3c72459cad69b58efacae6b341227b21_lbedjf.jpg',
            email='2151010425Tu@ou.edu.vn',
            phone='0123456789')
        user3 = User(
            role=UserRole.CUSTOMER,
            username='huutu',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            avatar='https://res.cloudinary.com/dg1zsnywc/image/upload/v1715678948/vzvrsl6fwwzyl9thtmn2.jpg',
            email='2@ou.edu.vn',
            phone='7312936921')
        user4 = User(
            role=UserRole.CUSTOMER,
            username='minhlong',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            avatar='https://res.cloudinary.com/dg1zsnywc/image/upload/v1715772103/il4g2k9ndrvvj187vkqg.jpg',
            email='trihuynh3103@gmail.com',
            phone='3485692348')
        user5 = User(
            role=UserRole.CUSTOMER,
            username='chanhkhoi',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            avatar='https://res.cloudinary.com/dg1zsnywc/image/upload/v1715772103/il4g2k9ndrvvj187vkqg.jpg',
            email='4@gmail.com',
            phone='31231234124')
        user6 = User(
            role=UserRole.CUSTOMER,
            username='trihuynh',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            avatar='https://res.cloudinary.com/dg1zsnywc/image/upload/v1708905744/ffkv6fef0gmw3dewytoq.jpg',
            email='5@gmail.com',
            phone='56978560756')
        user7 = User(username='tu2512', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                     role=UserRole.RECEPTIONIST, email='6@gmail.com', phone='8354084534324', gender=False)
        db.session.commit()
        db.session.add_all([user1, user2, user3, user4, user5, user6, user7])
        db.session.commit()

        admin1 = Administrator(id=1, name='Trí Huỳnh')
        db.session.add(admin1)
        db.session.commit()

        Receptionist1 = Receptionist(name='Thiên Tú', id=7)
        db.session.add(Receptionist1)
        db.session.commit()

        ct1 = CustomerType()
        ct2 = CustomerType(type='FOREIGN')
        db.session.add_all([ct1, ct2])
        db.session.commit()

        cus1 = Customer(id=2, name='Đổng Thiên Tú', identification='1231234124', customer_type_id=1)
        cus2 = Customer(id=3, name='Nguyễn Hữu Tú', identification='3453456347', customer_type_id=1)
        cus3 = Customer(id=4, name='Lê Duy Minh Long', identification='7567657567', customer_type_id=2)
        cus4 = Customer(id=5, name='Nguyễn Chánh Khôi', identification='34534578', customer_type_id=2)
        cus5 = Customer(id=6, name='Huỳnh Võ Đức Trí', identification='46457457323', customer_type_id=1)
        db.session.add_all([cus1, cus2, cus3, cus4, cus5])
        db.session.commit()

        ##################

        ct_reg1 = CustomerTypeRegulation(admin_id=1, customer_type_id=1)
        ct_reg2 = CustomerTypeRegulation(admin_id=1, customer_type_id=2, rate=1.5)
        db.session.add_all([ct_reg1, ct_reg2])
        db.session.commit()

        room_reg1 = RoomRegulation(room_type_id=1, admin_id=1, room_quantity=10, capacity=3, price=7000000)
        room_reg2 = RoomRegulation(room_type_id=2, admin_id=1, room_quantity=15, capacity=5, price=9000000)
        room_reg3 = RoomRegulation(room_type_id=3, admin_id=1, room_quantity=20, capacity=7, price=12000000)
        db.session.add_all([room_reg1, room_reg2, room_reg3])
        db.session.commit()

        #####################

        cm1 = Comment(customer_id=2, content='Khách sạn này tuyệt vời thật!',
                      created_date=datetime(2024, 3, 31, 13, 31), room_id=1)

        cm2 = Comment(customer_id=3, content='Thật bất ngờ vì vẻ đẹp của khách sạn!',
                      created_date=datetime(2024, 2, 4, 15, 3), room_id=1)

        cm3 = Comment(customer_id=4, content='sẽ ủng hộ nhiều ạ =)))))',
                      created_date=datetime(2024, 5, 6, 12, 4), room_id=2)

        cm4 = Comment(customer_id=5, content='Một trải nghiệm thật tuyệt vời',
                      created_date=datetime(2023, 6, 19, 21, 45), room_id=2)

        cm5 = Comment(customer_id=6,content='I love your Hotel',
                      created_date=datetime(2024, 1, 31, 8, 20),room_id=2)

        cm6 = Comment(customer_id=2,content='chất lượng tuyệt vời',
                      created_date=datetime(2024, 3, 1, 20, 8),room_id=3)

        cm7 = Comment(customer_id=3, content='thoải mái , bình yên , lãng mạn',
                      created_date=datetime(2024, 3, 6, 15, 56), room_id=3)

        cm8 = Comment(customer_id=4, content='Thật là một nơi đáng để nghỉ dưỡng',
                      created_date=datetime(2023, 8, 13, 17, 5), room_id=3)

        cm9 = Comment(customer_id=5, content='Xứng đáng với số tiền bỏ ra',
                      created_date=datetime(2023, 12, 12, 12, 12),room_id=3)

        cm10 = Comment(customer_id=6,content='Nhân viên lễ tân cute xĩu ^^',
                       created_date=datetime(2023, 11, 11, 11, 11),room_id=3)

        cm11 = Comment(customer_id=2,content='địa điểm đáng để chú ý trong kì kĩ dưỡng sắp tới của bạn!',
                       created_date=datetime(2023, 12, 21, 12, 12),room_id=4)

        cm12 = Comment(customer_id=3, content='không có gì để chê',
                       created_date=datetime(2023, 8, 8, 8, 8), room_id=4)

        cm13 = Comment(customer_id=4, content='Nơi này rất thoải mái và tiện nghi, có view đỉnh lắm ạ!',
                       created_date=datetime(2023, 7, 7, 7, 7), room_id=4)

        cm14 = Comment(customer_id=5, content='đi đi mọi người khách sạn tuyệt phẩm',
                       created_date=datetime(2023, 11, 30, 6, 12), room_id=4)

        cm15 = Comment(customer_id=6, content='tư vấn phòng này và trải nghiệm rất tốt',
                       created_date=datetime(2024, 2, 9, 15, 18), room_id=4)

        cm16 = Comment(customer_id=2,content='phòng rộng rãi, sạch sẽ, thơm tho',
                       created_date=datetime(2024, 1, 9, 17, 1),room_id=5)

        cm17 = Comment(customer_id=3,content='thanh toán thật dễ dàng',
                       created_date=datetime(2024, 2, 28, 12, 15),room_id=5)

        cm18 = Comment(customer_id=4,content='Luxury Hotel <3',
                       created_date=datetime(2023, 8, 31, 9, 21),room_id=5)
        db.session.add_all([cm1, cm2, cm3,
                            cm4, cm5, cm6,
                            cm7, cm8, cm9,
                            cm10, cm11, cm12,
                            cm13, cm14, cm15,
                            cm16, cm17, cm18])
        db.session.commit()

        reservation_data = [
            {'customer_id': 2, 'receptionist_id': 7, 'room_id': 4,
             'checkin_date': datetime(2024, 1, 31, 20, 15),
             'checkout_date': datetime(2024, 2, 28, 15, 20), 'deposit': 9000000},

            {'customer_id': 1, 'receptionist_id': 7, 'room_id': 2,
             'checkin_date': datetime(2024, 3, 25, 21, 10),
             'checkout_date': datetime(2024, 3, 29, 10, 21), 'deposit': 15000000},

            {'customer_id': 2, 'receptionist_id': 7, 'room_id': 2,
             'checkin_date': datetime(2023, 12, 11, 13, 21),
             'checkout_date': datetime(2023, 12, 21, 21, 13), 'deposit': 5000000},

            {'customer_id': 1, 'receptionist_id': 7, 'room_id': 1,
             'checkin_date': datetime(2024, 1, 18, 16, 30),
             'checkout_date': datetime(2024, 2, 29, 3, 4), 'deposit': 15000000},

            {'customer_id': 4, 'receptionist_id': 7, 'room_id': 1,
             'checkin_date': datetime(2024, 5, 3, 17, 5),
             'checkout_date': datetime(2024, 5, 8, 5, 17), 'deposit': 10000000},

            {'customer_id': 5, 'receptionist_id': 7, 'room_id': 2,
             'checkin_date': datetime(2023, 2, 21, 9, 15),
             'checkout_date': datetime(2023, 3, 19, 15 ,9), 'deposit': 18500000},

            {'customer_id': 2, 'receptionist_id': 7, 'room_id': 1,
             'checkin_date': datetime(2023, 7, 21, 17, 12),
             'checkout_date': datetime(2023, 8, 21, 12, 17), 'deposit': 20000000},
        ]

        for data in reservation_data:
            reservation = Reservation(**data)
            db.session.add(reservation)
        db.session.commit()

        # Tạo đối tượng RoomRental và thêm dữ liệu chi tiết
        room_rental1 = RoomRental(
            receptionist_id=7,
            room_id=4,
            reservation_id=1,
            checkin_date=datetime(2024, 3, 17, 11, 33, 12),
            checkout_date=datetime(2024, 5, 21, 12, 44, 51),
            deposit=5000000,
            is_paid=True
        )

        room_rental2 = RoomRental(
            receptionist_id=7,
            room_id=2,
            reservation_id=2,
            checkin_date=datetime(2024, 3, 8, 12, 45, 1),
            checkout_date=datetime(2024, 3, 21, 21, 6, 8),
            deposit=None,
            is_paid=True
        )

        room_rental3 = RoomRental(
            receptionist_id=7,
            room_id=3,
            checkin_date=datetime(2024, 4, 3, 20, 22, 17),
            checkout_date=datetime(2024, 5, 16, 9, 23, 12),
            deposit=21000000,
            is_paid=True
        )

        room_rental4 = RoomRental(
            receptionist_id=7,
            room_id=2,
            reservation_id=3,
            checkin_date=datetime(2024, 2, 27, 18, 1, 25),
            checkout_date=datetime(2024, 3, 7, 15, 32, 11),
            deposit=8000000,
            is_paid=True
        )

        room_rental5 = RoomRental(
            receptionist_id=7,
            room_id=1,
            reservation_id=4,
            checkin_date=datetime(2024, 8, 3, 6, 3, 24),
            checkout_date=datetime(2024, 8, 24, 8, 6, 12),
            deposit=10000000,
            is_paid=True
        )

        room_rental6 = RoomRental(
            receptionist_id=7,
            room_id=1,
            reservation_id=5,
            checkin_date=datetime(2024, 1, 20, 9, 22, 32),
            checkout_date=datetime(2024, 2, 3, 21, 44, 23),
            deposit=None,
            is_paid=True
        )

        room_rental7 = RoomRental(
            receptionist_id=7,
            room_id=3,
            checkin_date=datetime(2024, 4, 12, 10, 2, 50),
            checkout_date=datetime(2024, 4, 26, 21, 5, 18),
            deposit=21000000,
            is_paid=True
        )

        room_rental8 = RoomRental(
            receptionist_id=7,
            room_id=2,
            reservation_id=6,
            checkin_date=datetime(2024, 6, 18, 7, 30, 21),
            checkout_date=datetime(2024, 3, 21, 9, 15, 21),
            deposit=None,
            is_paid=True
        )

        room_rental9 = RoomRental(
            receptionist_id=7,
            room_id=1,
            reservation_id=7,
            checkin_date=datetime(2024, 2, 9, 8, 20, 5),
            checkout_date=datetime(2024, 3, 10, 20, 8, 8),
            deposit=15000000,
            is_paid=True
        )

        # Thêm các đối tượng vào cơ sở dữ liệu
        with db.session.begin():
            db.session.add_all(
                [room_rental1, room_rental2, room_rental3, room_rental4, room_rental5, room_rental6, room_rental7,
                 room_rental8, room_rental9])

        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()

        receipt_data = [
            {'receptionist_id': 7, 'rental_room_id': 1, 'total_price': 5000000,
             'created_date': datetime(2024, 5, 21, 12, 45)},

            {'receptionist_id': 7, 'rental_room_id': 2, 'total_price': 3000000,
             'created_date': datetime(2024, 3, 21, 21, 6)},

            {'receptionist_id': 7, 'rental_room_id': 3, 'total_price': 21000000,
             'created_date': datetime(2024, 5, 16, 9, 23)},

            {'receptionist_id': 7, 'rental_room_id': 4, 'total_price': 8000000,
             'created_date': datetime(2024, 2, 3, 21, 45)},

            {'receptionist_id': 7, 'rental_room_id': 5, 'total_price': 12000000,
             'created_date': datetime(2024, 8, 24, 8, 6)},

            {'receptionist_id': 7, 'rental_room_id': 6, 'total_price': 3000000,
             'created_date': datetime(2024, 2, 3, 9, 44)},

            {'receptionist_id': 7, 'rental_room_id': 7, 'total_price': 21000000,
             'created_date': datetime(2024, 4, 26, 9, 5)},

            {'receptionist_id': 7, 'rental_room_id': 8, 'total_price': 3000000,
             'created_date': datetime(2024, 3, 21, 9, 15)},

            {'receptionist_id': 7, 'rental_room_id': 9, 'total_price': 15000000,
             'created_date': datetime(2024, 3, 10, 20, 8)},
        ]

        for data in receipt_data:
            receipt = Receipt(**data)
            db.session.add(receipt)

        db.session.commit()
