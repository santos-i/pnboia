from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from application.blueprints.forms import LoginForm, RegisterForm
from application.extensions.database import db
from application.models import User
import pandas as pd


def init_app(app):
        
    @app.route('/')
    def home():
        text = 'text'
        
        return render_template('home.html', text=text)

    @app.route('/<id>')
    @login_required
    def generic(id=None):
        text = f'{id}'
        
        return render_template('buoy.html', text=text)


    @app.route('/buoy-table')
    @login_required
    def table():

        buoyStatus = pd.read_sql('buoyStatus', db.engine).drop(columns=['index'])
        print(buoyStatus)
        
        return render_template(
            'table.html', 
            data_values=buoyStatus.values,
            data_headings = buoyStatus.columns.values,
        )



    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()    
            if user:
                check_pass = user.check_password(form.password.data)
            
            if user is None or not check_pass:
                flash('Invalid credentials')
                return redirect(url_for('login'))

            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('table')
            return redirect(next_page)
        return render_template('login.html', form=form)


    @app.route('/logout')
    def logout():
        session.pop('username', None)
        logout_user()
        return redirect(url_for('home'))
    

    @app.route('/signup', methods=['GET','POST'])
    def signup():

        form = RegisterForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                flash('The user already exists')
            else:
                new_user = User(username=form.username.data, password=form.password1.data)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
        elif form.password1.data != form.password2.data:
                flash('Passwords do no match!')

        return render_template('signup.html', form=form,)


    @app.route('/newpass')
    def password():
        form = LoginForm()
        return render_template('password.html', form=form)