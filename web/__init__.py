from flask import Flask
from flask_mysqldb import MySQL
import cloudinary
import cloudinary.uploader

mysql = MySQL()

def create_app():
    app = Flask(__name__)

    app.config['MYSQL_HOST'] = 'localhost'  
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'angie'
    app.config['MYSQL_DB'] = 'webssis'

    app.secret_key = 'graaah'

    mysql.init_app(app)

    cloudinary.config( 
    cloud_name = "dygsi9hr5", 
    api_key = "259755552848519", 
    api_secret = "w-i9j_axYRmHkjkQVgZLJt1EQfk", 
    secure=True
)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    return app
