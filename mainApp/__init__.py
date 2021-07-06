from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app=Flask(__name__)

bootstrap=Bootstrap(app)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'nityaak5@gmail.com'
app.config['MAIL_PASSWORD'] = 'Alohorma05*'

mail=Mail(app) 

db= SQLAlchemy(app)
bcrypt= Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='loginForm'
login_manager.login_message_category='info'      #to improve the look 
from mainApp import routes
 