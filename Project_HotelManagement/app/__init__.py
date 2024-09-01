from urllib.parse import quote

import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
login = LoginManager(app)

app.secret_key = 'kfshafeoiuhfweiafhewuo12312@!78235217841'
app.config['SQLALCHEMY_DATABASE_URI'] = str.format('mysql+pymysql://trihuynh:%s@trihuynh.mysql.database.azure.com/hoteldb?charset=utf8mb4'
                                                   % quote('Toiyeuyasuo123'))
# app.secret_key = 'kfshafeoiuhfweiafhewuo12312@!78235217841'
# app.config['SQLALCHEMY_DATABASE_URI'] = str.format('mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4'
#                                                    % quote('123456'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4

db = SQLAlchemy(app=app)

cloudinary.config(
    cloud_name='dg1zsnywc',
    api_key='275498577249468',
    api_secret='onpq_zM83tw8n6qHCp8cAA8jqsg'
)

# Các thông số cần thiết từ tài khoản VNPay Sandbox
vnpay_config = {
    'vnp_TmnCode': 'SXFFWHYF',
    'vnp_HashSecret': 'DI2LQWIL88MDU181O7G1I0UUKKGP0631',
    'vnp_Url': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
}
