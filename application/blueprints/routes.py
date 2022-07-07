from turtle import title
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from application.blueprints.forms import LoginForm, RegisterForm
from application.extensions.database import db
from application.models import User

import plotly.graph_objects as go
import pandas as pd




def init_app(app):
        
    @app.route('/')
    def home():
        text = 'text'
        
        return render_template('home.html', text=text)

    @app.route('/<buoy>')
    @login_required
    def generic(buoy=None):

        outrafig = go.Figure(go.Scattermapbox(
            mode = "markers+lines",
            lon = [10, 20, 30],
            lat = [10, 20,30],
            marker = {'size': 10}))

        outrafig.add_trace(go.Scattermapbox(
            mode = "markers+lines",
            lon = [-50, -60,40],
            lat = [30, 10, -20],
            marker = {'size': 10}))

        outrafig.update_layout(
            margin ={'l':0,'t':0,'b':0,'r':0},
            mapbox = {
                'center': {'lon': 10, 'lat': 10},
                'style': "stamen-terrain",
                'center': {'lon': -20, 'lat': -20},
                'zoom': 1})

        outrafig = outrafig.to_html(full_html=False)

        return render_template(
            'buoy.html', 
            buoy=buoy,
            div_placeholder=outrafig,

        )


    @app.route('/<buoy>/<type>')
    @login_required
    def generic2(buoy=None, type=None):
        
        
        return render_template(
            'buoy2.html', 
            buoy=buoy,
        )


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