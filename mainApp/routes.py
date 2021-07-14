import os
import secrets
from PIL import Image
from flask import render_template, flash, session, redirect, url_for, request, abort
from mainApp.models import User, Post
from mainApp.myForm import NameForm, LoginForm, UpdateAccountForm, PostForm, ResetPasswordForm, requestResetForm
from flask_mail import Message
from mainApp import app, mail,db,bcrypt
from flask_login import login_user, current_user, logout_user, login_required
   
@app.route('/')
def index():
    page=request.args.get('page',1, type=int)
    posts=Post.query.paginate(per_page=2, page=page)
    return render_template('index.html', posts=posts)


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


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title= form.title.data, content= form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post has been created.", 'success')
        return redirect(url_for('index'))
    return render_template('new_post.html', form=form)


@app.route('/post/<post_id>')
def post(post_id):
    post= Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route('/post/<post_id>/update',methods=['GET', 'POST'])
def update_post(post_id):
    post= Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', form=form)
    
    
@app.route("/post/<int:post_id>/delete", methods=['GET','POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))



@app.route("/user/<string:username>")
def user_post(username):
    page=request.args.get('page',1, type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .paginate(per_page=2, page=page)
    return render_template('user_post.html', posts=posts, user=user)


def send_reset_email(user):
    token= user.get_reset_token()
    msg= Message("Reset Password", sender="nityaak5@gmail.com" ,recipients=['nityaak5@gmail.com'])
#    f string need only one curly brace not two
    msg.body= f''' To reset:
    {url_for('reset_token', token=token, _external = True)}

    If you did not make this request, ignore.

    '''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form= requestResetForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email= form.email.data).first()
        send_reset_email(user)
        flash("Email Sent", "info")
        return redirect(url_for('loginForm'))


    return render_template('reset_request.html', form=form)



@app.route("/reset_password/<token>", methods=['GET', 'POST'])

def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user= User.verify_reset_token(token)                         #will return a user id

    if user is None:
        flash("Invalid or expired token", 'warning')
        return redirect(url_for('reset_request'))
    form= ResetPasswordForm()
    if form.validate_on_submit():
      
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # using the database
        
        user.password= hashed_password
   
        db.session.commit()
        
        flash(f'Updated', 'success')
        return redirect(url_for("loginForm"))
    return render_template('reset_token.html', form= form)



