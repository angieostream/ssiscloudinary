from flask import Flask
from flask_mysqldb import MySQL
import cloudinary
from dotenv import load_dotenv
import os

mysql = MySQL()

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)

    app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'localhost')  
    app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '')
    app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'webssis')

    app.secret_key = os.getenv('SECRET_KEY', 'graaah')

    mysql.init_app(app)

    # Configure Cloudinary using env variables
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )

    from .controller import views
    from .controllers.students_controller import students_bp
    from .controllers.colleges_controller import colleges_bp
    from .controllers.programs_controller import programs_bp

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(colleges_bp, url_prefix='/colleges')
    app.register_blueprint(programs_bp, url_prefix='/programs')

    return app
