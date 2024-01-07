from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager
from urllib.parse import quote
from flask_babel import Babel
#from flask_babelex import Babel


app = Flask(__name__)
app.secret_key = '&%V%@&(V%@%C%C#X%$%'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hospitalitymanagement?charset=utf8mb4" % quote('Vuphat12345')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 1
app.config['COMMENT_SIZE'] = 8

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

babel = Babel(app)





cloudinary.config(
    cloud_name='dlhnmdyta',
    api_key='344944847395468',
    api_secret='UCHeQjSO9h8SuUhIiwqEcN1YRAs'
)