import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from mainApp import mail


def save_picture(form_picture):
    # _ means f_name actually
    random_hex=secrets.token_hex(8)
    _, f_ext= os.path.splitext(form_picture.filename)   
    picture_fn= random_hex+ f_ext
    picture_path= os.path.join(current_app.root_path, 'static/profile_pics',picture_fn)

    output_size=(125,125)
    i= Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def send_reset_email(user):
    token= user.get_reset_token()
    msg= Message("Reset Password", sender="nityaak5@gmail.com" ,recipients=['nityaak5@gmail.com'])
#    f string need only one curly brace not two
    msg.body= f'''To reset:
    {url_for('users.reset_token', token=token, _external = True)}

    If you did not make this request, ignore.'''
    mail.send(msg)