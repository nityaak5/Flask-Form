import os
from flask import Flask, render_template,flash,redirect, url_for, session
from form import NameForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

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




#The database

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return f"(Role: {self.name})"

class User(db.Model):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password=db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    

    def __repr__(self):
        return f"(Name: {self.username}, ID: {self.id}, Password: {self.password})"
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    form=NameForm()
    if form.validate_on_submit():
        # using the database
        user=User.query.filter_by(username=form.username.data).first()

        if user is None:
            user=User(username=form.username.data, password= form.password.data)
            db.session.add(user)
            db.session.commit()
            session['known']=False
            
           
            msg=Message("Hi", sender='nityaak5@gmail.com', recipients=['nityaak5@gmail.com'])
            msg.body="Test Body"
            mail.send(msg)
        else:
            session['known']=True

        session['username']=form.username.data
        
        flash(f'Account created for {form.username.data}!', 'success')
        return render_template('index.html', username=session.get('username'), known=session.get('known',False))
        # return redirect(url_for('index',name=session.get('username'),kn=session.get('known',False)))
    return render_template('myform.html', form=form,)


if __name__=='__main__':
    app.run(debug=True)