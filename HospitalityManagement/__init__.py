from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babelex import Babel
import cloudinary
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key = '&%V%@&(V%@%C%C#X%$%'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Vuphat12345@localhost/hospitalitymanagement?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 1
app.config['COMMENT_SIZE'] = 8

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

babel = Babel(app=app)
@babel.localeselector
def get_locale():
    return ''


cloudinary.config(
    cloud_name='',
    api_key='',
    api_secret=''
)