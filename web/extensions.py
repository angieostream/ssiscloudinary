from flask_mysqldb import MySQL
import cloudinary

mysql = MySQL()

def init_cloudinary():
    cloudinary.config( 
        cloud_name = "dygsi9hr5", 
        api_key = "259755552848519", 
        api_secret = "w-i9j_axYRmHkjkQVgZLJt1EQfk", 
        secure=True
    )
