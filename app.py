"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash
from models import db, connect_db, User, Post, Tag, PostTag

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
    
    return redirect(f'/posts/{new_post.id}')

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    '''Display post from user'''
    post = Post.query.get_or_404(post_id)
    title = post.title
    content = post.content
    
    user_id = post.user_id
    user = User.query.get_or_404(user_id)
    
    return render_template('post_details.html', title=title, content=content, user=user, post=post)

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    '''Delete a user from db'''
    post = Post.query.get_or_404(post_id)
    user_id = post.user_id
    user = User.query.get_or_404(user_id)
    
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    return redirect(f'/users/{user.id}')

@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
    '''Show form to edit current post'''
    post = Post.query.get_or_404(post_id)
    return render_template('edit_post.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def edit_post(post_id):
    '''Change details of a post'''
    post = Post.query.get(post_id)
    user_id = post.user_id
    user = User.query.get_or_404(user_id)
    created_at = post.created_at
    title = request.form.get('title')
    content = request.form.get('content')
    id = post.id
    
    if not title:
        title = post.title
    if not content:
        content = post.content
        
    post.content = content
    post.title = title
    post.user_id = user_id
    post.created_at = created_at
    post.id = id
    
    db.session.add(post)
    db.session.commit()
    return redirect(f'/posts/{post.id}')

### SECTION FOR ADDING TAGS ###

@app.route('/tags')
def list_tags():
    '''Show all tags with links to tag details page'''
    tags = Tag.query.all()
    return render_template('tag_list.html', tags=tags)

@app.route('/tags/new')
def show_tag_form():
    '''Display form to submit a new tag'''
    return render_template('new_tag.html')

@app.route('/tags/new', methods=["POST"])
def create_tag():
    '''Add new tag to db and display it'''
    name = request.form.get('tag')
    
    new_tag = Tag(name=name)
    db.session.add(new_tag)
    db.session.commit()
    
    return redirect(f'/tags')

@app.route('/tags/<int:tag_id>')
def show_posts_from_tag(tag_id):
    '''View all posts that have been tagged'''
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag_details.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit')
def edit_tag_form(tag_id):
    '''Show form to edit an existing tag'''
    tag = Tag.query.get_or_404(tag_id)
    return render_template('edit_tag.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def edit_tag(tag_id):
    '''Update tag in db and return to tag details page'''
    tag = Tag.query.get_or_404(tag_id)
    name = request.form.get('tag')

    if not name:
        name = tag.name
        
    tag.name = name
    db.session.add(tag)
    db.session.commit()
    
    return redirect(f'/tags/{tag.id}')

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    '''delete a tag from db'''
    tag = Tag.query.get_or_404(tag_id)
    Tag.query.filter_by(id=tag_id).delete()
    db.session.commit()
    
    return redirect('/tags')