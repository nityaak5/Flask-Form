
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from mainApp import db, bcrypt
from mainApp.models import User, Post
from mainApp.users.forms import (NameForm, LoginForm, UpdateAccountForm,
                                   requestResetForm, ResetPasswordForm)
from mainApp.users.utils import save_picture, send_reset_email




users= Blueprint('users', __name__)
 



@users.route('/form', methods=['GET', 'POST'])
def form():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
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
        return redirect(url_for("users.loginForm"))
        # return redirect(url_for('index',name=session.get('username'),kn=session.get('known',False)))
    return render_template('myform.html', form=form)



@users.route('/loginform', methods=['GET', 'POST'])
def loginForm():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page= request.args.get('next')   #to get profile, dont use square bracket with dict args- error. get gives none

            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        
        else:
            flash('Incorrect Email or Password', 'danger')
    return render_template('loginForm.html', form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@users.route('/profile', methods=['GET', 'POST'])
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
        return redirect(url_for('users.profile'))
    elif request.method== 'GET':
        form.username.data= current_user.username
        form.email.data=current_user.email
    image_file= url_for('static', filename= 'profile_pics/'+ current_user.image_file)

    return render_template('profile.html', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_post(username):
    page=request.args.get('page',1, type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .paginate(per_page=2, page=page)
    return render_template('user_post.html', posts=posts, user=user)





@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form= requestResetForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email= form.email.data).first()
        send_reset_email(user)
        flash("Email Sent", "info")
        return redirect(url_for('users.loginForm'))


    return render_template('reset_request.html', form=form)



@users.route("/reset_password/<token>", methods=['GET', 'POST'])

def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user= User.verify_reset_token(token)                         #will return a user id

    if user is None:
        flash("Invalid or expired token", 'warning')
        return redirect(url_for('users.reset_request'))
    form= ResetPasswordForm()
    if form.validate_on_submit():
      
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # using the database
        
        user.password= hashed_password
   
        db.session.commit()
        
        flash(f'Updated', 'success')
        return redirect(url_for("users.loginForm"))
    return render_template('reset_token.html', form= form)

