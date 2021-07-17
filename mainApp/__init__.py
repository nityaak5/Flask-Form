from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from mainApp.config import Config

mail=Mail() 
db= SQLAlchemy()
bcrypt= Bcrypt()
login_manager=LoginManager()
login_manager.login_view='users.loginForm'
login_manager.login_message_category='info'      #to improve the look 


def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from mainApp.users.routes import users
    from mainApp.posts.routes import posts
    from mainApp.main.routes import main
    from mainApp.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    
    return app



