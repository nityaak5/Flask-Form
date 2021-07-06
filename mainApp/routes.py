from flask import render_template, flash, session, redirect, url_for, request
from mainApp.models import Role, User
from mainApp.myForm import NameForm, LoginForm
from flask_mail import Message
from mainApp import app, mail,db,bcrypt
from flask_login import login_user, current_user, logout_user, login_required
   
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form=NameForm()
    if form.validate_on_submit():
    # utf-8 for string instead of bytes
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # using the database
        
        user=User(username=form.username.data, password= hashed_password, email=form.email.data)
        db.session.add(user)
        db.session.commit()

           
        msg=Message("Hi", sender='nityaak5@gmail.com', recipients=['nityaak5@gmail.com'])
        msg.body="Test Body"
        mail.send(msg)
        
        flash(f'Account created for {form.username.data}! You can now log in', 'success')
        return redirect(url_for("loginForm"))
        # return redirect(url_for('index',name=session.get('username'),kn=session.get('known',False)))
    return render_template('myform.html', form=form)



@app.route('/loginform', methods=['GET', 'POST'])
def loginForm():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page= request.args.get('next')   #to get profile, dont use square bracket with dict args- error. get gives none

            return redirect(next_page) if next_page else redirect(url_for("index"))
        
        else:
            flash('Incorrect Email or Password', 'danger')
    return render_template('loginForm.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')