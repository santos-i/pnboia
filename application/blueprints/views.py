from flask import render_template, flash, redirect, url_for, session, request, abort
from application.blueprints.forms import LoginForm, RegisterForm
from application.extensions.database import db
from application.models import User
from application.extensions.auth import login_manager
from flask_login import login_user, login_required, logout_user



def init_app(app):

    @app.route('/home')
    @login_required
    def home():
        return redirect(url_for('dash'))

    @app.route('/dash/')
    @login_required
    def dash():
        # return dash_app.index()
        return 'a'


    @app.route('/', methods=['GET','POST'])
    def login():
        error=None
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and login_user(user):
                return redirect(url_for('home')) 
            else:
                error = 'Invalid credentials'    
            
        return render_template('login.html', form=form, error=error)

    
    @app.route('/signup', methods=['GET','POST'])
    def signup():
        error = None
        form = RegisterForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                error = 'The user already exists'
            else:
                new_user = User(username=form.username.data, password=form.password1.data)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
        elif form.password1.data != form.password2.data:
                error = 'Passwords do no match!'

        return render_template('signup.html', form=form, error=error)


    @app.route('/logout')
    def logout():
        session.pop('username', None)
        logout_user()
        return redirect(url_for('login'))
