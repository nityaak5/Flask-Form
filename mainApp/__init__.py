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


<<<<<<< HEAD
def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(Config)
=======
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = email
app.config['MAIL_PASSWORD'] = password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
>>>>>>> b07fbb4a9f0335e64a9ff10fc464dd5da72aa667

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from mainApp.users.routes import users
    from mainApp.posts.routes import posts
    from mainApp.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    
    return app


