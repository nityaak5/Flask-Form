import os
import secrets
from PIL import Image
from flask import render_template, flash, session, redirect, url_for, request
from mainApp.models import Role, User
from mainApp.myForm import NameForm, LoginForm, UpdateAccountForm
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


def save_picture(form_picture):
    # _ means f_name actually
    random_hex=secrets.token_hex(8)
    _, f_ext= os.path.splitext(form_picture.filename)   
    picture_fn= random_hex+ f_ext
    picture_path= os.path.join(app.root_path, 'static/profile_pics',picture_fn)

    output_size=(125,125)
    i= Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form= UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file= save_picture(form.picture.data)
            current_user.image_file= picture_file

        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash("Details updated!", 'success')
        return redirect(url_for('profile'))
    elif request.method== 'GET':
        form.username.data= current_user.username
        form.email.data=current_user.email
    image_file= url_for('static', filename= 'profile_pics/'+ current_user.image_file)

    return render_template('profile.html', image_file=image_file, form=form)