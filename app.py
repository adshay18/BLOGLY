"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash
from models import db, connect_db, User, Post

from flask_debugtoolbar import DebugToolbarExtension

'''Configure app, currently development mode'''
app = Flask(__name__)
app.config['SECRET_KEY'] = "blogly"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

debug = DebugToolbarExtension(app)

@app.route('/')
def redirect_to_users():
    '''Redirect to /users'''
    return redirect('/users')

@app.route('/users')
def list_users():
    '''Show list of all users in the db'''
    users = User.query.all()
    return render_template('list.html', users=users)

@app.route('/users/new')
def show_form():
    '''Show form to add a new user'''
    return render_template('new_user.html')
    
@app.route('/users/new', methods=["POST"])
def generate_new_user():
    '''Capture form data and add new user to db'''
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"]
    
    if not image_url:
        image_url = 'https://bitsofco.de/content/images/2018/12/broken-1.png'
    if not first_name:
        flash('Users must have both a First Name and a Last Name, please try again.')
        return render_template('new_user.html')
    if not last_name:
        flash('Users must have both a First Name and a Last Name, please try again.')
        return render_template('new_user.html')
    
    new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()
    
    return redirect(f'/users/{new_user.id}')

@app.route('/users/<int:user_id>')
def show_user(user_id):
    '''Show name and profile pic of a user'''
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter(Post.user_id == user.id).all()
    return render_template("user_details.html", user=user, posts=posts)

@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    '''Edit details for a user'''
    user = User.query.get_or_404(user_id)
    return render_template('edit_user.html', user=user)
    
@app.route('/users/<int:user_id>/edit', methods=["POST"])
def change_user(user_id):
    '''Update user information in db and display it correctly'''
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    image_url = request.form.get("image_url")
    user = User.query.get_or_404(user_id)
    
    if not first_name:
        first_name = user.first_name
    if not last_name:
        last_name = user.last_name
    if not image_url:
        image_url = user.image_url
    
    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image_url
    
    db.session.add(user)
    db.session.commit()
   
    return redirect(f'/users/{user_id}')
    
@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    '''Delete a user from db'''
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect('/')


# Section for creating posts ***************

@app.route('/users/<int:user_id>/posts/new')
def show_posts_form(user_id):
    '''Show form to add a new post'''
    user = User.query.get_or_404(user_id)
    return render_template('new_post.html', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def add_post(user_id):
    '''Create post and add to db'''
    user = User.query.get_or_404(user_id)
    title = request.form.get("title")
    content = request.form.get("content")
    
    new_post = Post(title=title, content=content, user_id=user.id)
    db.session.add(new_post)
    db.session.commit()
    
    return redirect('/')