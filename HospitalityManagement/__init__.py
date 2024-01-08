from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager
from urllib.parse import quote
from flask_babel import Babel

app = Flask(__name__)
app.secret_key = '&%V%@&(V%@%C%C#X%$%'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hospitalitymanagement?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 1
app.config['COMMENT_SIZE'] = 8

db = SQLAlchemy(app=app)
login = LoginManager(app=app)
babel = Babel(app)

cloudinary.config(
    cloud_name='dgm68hajt',
    api_key='445342655699255',
    api_secret='-RkgzrKOgwbd32E9oK71iOW_WDQ'
)