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
    def generic(buoy):


        BUOYS = [
            'noronha',
            'alcatrazes',
            'mexilhao',
            'bc1',
            'keller',
            'pinguim',
            '_potter',
            'abrolhos',
            'trindade',
            'bmo_santos',
            'antartica',
            'minuano',
            'itaguai',
            'itaoca',
            'niteroi2',
            'fortaleza',
            'vitoria',
            'cabofrio2',
            'niteroi',
            'santos',
            'itajai',
            'riogrande',
            'recife',
            'portoseguro',
            'cabofrio',
        ]

        if buoy in BUOYS:
            df = pd.read_sql(buoy, db.engine)
###############################################################################################################
            import plotly.graph_objects as go

            fig = go.Figure(go.Scattermapbox(
                mode = "markers+lines",
                lon = df['lon'],
                lat = df['lat'],
                marker = {
                    'color':'red',
                    'size': 5},
            ))


            fig.update_layout(
                margin ={'l':250,'t':0,'b':0,'r':250},
                mapbox = {
                    'style': "stamen-terrain",
                    'center': {'lon': 0, 'lat': 0},
                    'zoom': 0.8})
                    
            fig = fig.to_html()

##################################################################################################################

            import numpy as np

            wind = go.Figure(go.Scatter(x=df['Datetime'], y=df['wspd']))
            if 'gust' in list(df.columns):
                wind.add_trace(go.Scatter(x=df.index, y=df['gust']))
            
            wind2 = wind.to_html()
            wave = wind.to_html() ##################################################

            windrose = go.Figure()

            windrose.add_trace(go.Barpolar(
                r=[77.5, 72.5, 70.0, 45.0, 22.5, 42.5, 40.0, 62.5],
                name='11-14 m/s',
                marker_color='rgb(106,81,163)'
            ))
            windrose.add_trace(go.Barpolar(
                r=[57.5, 50.0, 45.0, 35.0, 20.0, 22.5, 37.5, 55.0],
                name='8-11 m/s',
                marker_color='rgb(158,154,200)'
            ))
            windrose.add_trace(go.Barpolar(
                r=[40.0, 30.0, 30.0, 35.0, 7.5, 7.5, 32.5, 40.0],
                name='5-8 m/s',
                marker_color='rgb(203,201,226)'
            ))
            windrose.add_trace(go.Barpolar(
                r=[20.0, 7.5, 15.0, 22.5, 2.5, 2.5, 12.5, 22.5],
                name='< 5 m/s',
                marker_color='rgb(242,240,247)'
            ))

            windrose.update_traces(text=['North', 'N-E', 'East', 'S-E', 'South', 'S-W', 'West', 'N-W'])
            windrose.update_layout(
                title='Wind Speed Distribution in Laurel, NE',
                font_size=16,
                legend_font_size=16,
                polar_radialaxis_ticksuffix='%',
                polar_angularaxis_rotation=90,

            )

            windrose2 = windrose.to_html()
            waverose = windrose.to_html() ##########################################################



            return render_template(
                'buoy.html', 
                buoy=buoy,
                div_map=fig,
                div_wind=wind2,
                div_windrose=windrose2,
                div_wave = wave,
                div_waverose = waverose,
            )
        return render_template('home.html')


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