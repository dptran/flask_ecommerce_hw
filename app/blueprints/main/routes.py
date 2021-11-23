from os import stat
from . import bp as app
from app import db
from flask import request, render_template, url_for, redirect, flash
from datetime import datetime
from app.blueprints.auth.models import User
from app.blueprints.main.models import Post
from flask_login import login_user, logout_user, current_user

@app.route('/')
def home():
    context = {
        'first_name': 'Derek',
        'last_name': 'Hawkins',
        'email': 'derekhcodingtemple.com',
        'posts': Post.query.order_by(Post.date_created.desc()).all()
    }
    return render_template('index.html', **context)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/new_post', methods=['POST'])
def create_new_post():
    status = request.form.get('user_status')

    if status:
        p = Post(body=status, user_id=current_user.get_id())
        db.session.add(p)
        db.session.commit()
        flash('You have successfully created a new post.', 'success')
    else:
        flash('You cannot post nothing', 'warning')
    return redirect(url_for('main.home'))