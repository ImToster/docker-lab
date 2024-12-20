from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import and_
from . import db
from .models import User

routes = Blueprint('routes', __name__)

# Create the home route
@routes.route('/')
def home():

    users = User.query.all()

    # Transform the data into dicts
    user_dicts_ls = [user.__dict__ for user in users]

    return render_template("index.html", data=user_dicts_ls)

@routes.route('/new', methods=['POST'])
def add_user():

    username = request.form['username']
    name = request.form['name']
    password = request.form['password']

    # Validate user information and handle errors gracefully
    errors = []
    if not username:
        errors.append('Username is required.')
    if not name:
        errors.append('Name is required.')
    if not password:
        errors.append('Password is required.')

    if errors:
        for error in errors:
            flash(error, category='error')
            return redirect(url_for('routes.home'))

    # Validate if a user with the username already exists
    existing_user = User.query.filter_by(username=username).first()

    if existing_user is not None:
        flash('Username already registered!', category='error')
        return redirect(url_for('routes.home'))
    else:
        new_user = User(username=username, name=name, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('User successfully added!', category='success')
        return redirect(url_for('routes.home'))


@routes.route('/edit/<string:id>')
def edit_user(id):

    user = User.query.get(id)
    return render_template('update.html', user=user)


@routes.route('/update/<string:id>', methods=['POST'])
def update_user(id):

    user = User.query.get(id)

    # Validate if a user with the username already exists and if the fields are filled
    if user:
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        existing_username = User.query.filter(and_(User.username == username, User.id != id)).first()
        if existing_username:
            flash('Username already registered!', category='error')
            return redirect(url_for('routes.edit_user', id=id))
        elif not username or not name or not password:
            flash('All fields must be filled!', category='error')
            return redirect(url_for('routes.edit_user', id=id))
        user.username = username
        user.name = name
        user.password = password
        db.session.commit()
        flash('User successfully updated!', category='success')
        return redirect(url_for('routes.home'))



@routes.route('/delete/<string:id>')
def delete_user(id):

    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User successfully deleted!', category='success')
    return redirect(url_for('routes.home'))