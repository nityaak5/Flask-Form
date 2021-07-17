from flask import render_template, request, Blueprint
from mainApp.models import Post

main= Blueprint('main', __name__)
 

@main.route('/')
def index():
    page=request.args.get('page',1, type=int)
    posts=Post.query.paginate(per_page=2, page=page)
    return render_template('index.html', posts=posts)





