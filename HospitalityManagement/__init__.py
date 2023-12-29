from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = '&%V%@&(V%@%C%C#X%$%'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hospitalitymanagement?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 1
app.config['COMMENT_SIZE'] = 8

db = SQLAlchemy(app=app)
login = LoginManager(app=app)


cloudinary.config(
    cloud_name='',
    api_key='',
    api_secret=''
)