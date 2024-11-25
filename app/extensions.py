# app/extensions.py
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

mail = Mail()
bcrypt = Bcrypt()
mysql = MySQL()
